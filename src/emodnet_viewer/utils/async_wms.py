"""
Async WMS fetching utilities with fallback to synchronous mode

This module provides asynchronous WMS capabilities fetching with graceful
degradation to synchronous mode if async dependencies are unavailable.
"""

import asyncio
from typing import List, Dict, Any, Optional, Callable
from .logging_config import get_logger

logger = get_logger("async_wms")

# Try to import async dependencies
try:
    import aiohttp
    ASYNC_AVAILABLE = True
    logger.info("Async HTTP support available (aiohttp installed)")
except ImportError:
    ASYNC_AVAILABLE = False
    logger.info("Async HTTP not available, will use synchronous mode")
    aiohttp = None


async def fetch_wms_capabilities_async(
    url: str,
    params: Dict[str, str],
    timeout: int = 10,
    session: Optional['aiohttp.ClientSession'] = None
) -> Optional[bytes]:
    """
    Fetch WMS capabilities asynchronously

    Args:
        url: WMS service base URL
        params: Query parameters for GetCapabilities request
        timeout: Request timeout in seconds
        session: Optional aiohttp session (creates new if None)

    Returns:
        XML content as bytes, or None on error
    """
    if not ASYNC_AVAILABLE:
        raise RuntimeError("Async support not available - install aiohttp")

    close_session = session is None

    try:
        if session is None:
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            session = aiohttp.ClientSession(timeout=timeout_obj)

        async with session.get(url, params=params) as response:
            if response.status == 200:
                content = await response.read()
                logger.debug(f"Successfully fetched {len(content)} bytes from {url}")
                return content
            else:
                logger.warning(f"WMS request to {url} failed with status {response.status}")
                return None

    except asyncio.TimeoutError:
        logger.warning(f"Timeout fetching capabilities from {url}")
        return None
    except Exception as e:
        logger.error(f"Error fetching capabilities from {url}: {e}")
        return None
    finally:
        if close_session and session:
            await session.close()


async def fetch_all_wms_async(
    endpoints: List[Dict[str, Any]],
    timeout: int = 10
) -> List[Optional[bytes]]:
    """
    Fetch multiple WMS endpoints concurrently

    Args:
        endpoints: List of endpoint configs with 'url', 'params', 'name'
        timeout: Request timeout in seconds

    Returns:
        List of XML content (same order as endpoints), None for failures
    """
    if not ASYNC_AVAILABLE:
        raise RuntimeError("Async support not available - install aiohttp")

    logger.info(f"Fetching {len(endpoints)} WMS endpoints concurrently")

    timeout_obj = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(timeout=timeout_obj) as session:
        tasks = [
            fetch_wms_capabilities_async(
                ep['url'],
                ep['params'],
                timeout,
                session
            )
            for ep in endpoints
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to None
        processed = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Endpoint {endpoints[i]['name']} failed: {result}")
                processed.append(None)
            else:
                processed.append(result)

        return processed


def fetch_all_wms_sync(
    endpoints: List[Dict[str, Any]],
    timeout: int = 10
) -> List[Optional[bytes]]:
    """
    Fetch multiple WMS endpoints synchronously (fallback mode)

    Args:
        endpoints: List of endpoint configs with 'url', 'params', 'name'
        timeout: Request timeout in seconds

    Returns:
        List of XML content (same order as endpoints), None for failures
    """
    import requests

    logger.info(f"Fetching {len(endpoints)} WMS endpoints synchronously (fallback mode)")

    results = []
    for ep in endpoints:
        try:
            response = requests.get(ep['url'], params=ep['params'], timeout=timeout)
            if response.status_code == 200:
                results.append(response.content)
                logger.debug(f"Successfully fetched {ep['name']}")
            else:
                logger.warning(f"{ep['name']} failed with status {response.status_code}")
                results.append(None)
        except Exception as e:
            logger.error(f"Error fetching {ep['name']}: {e}")
            results.append(None)

    return results


def fetch_all_wms(
    endpoints: List[Dict[str, Any]],
    timeout: int = 10,
    prefer_async: bool = True
) -> List[Optional[bytes]]:
    """
    Fetch multiple WMS endpoints with automatic fallback

    Tries async mode if available and preferred, falls back to sync mode.

    Args:
        endpoints: List of endpoint configs with 'url', 'params', 'name'
        timeout: Request timeout in seconds
        prefer_async: If True, use async mode when available

    Returns:
        List of XML content (same order as endpoints), None for failures
    """
    if prefer_async and ASYNC_AVAILABLE:
        try:
            # Run async code in new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(fetch_all_wms_async(endpoints, timeout))
            finally:
                loop.close()
        except Exception as e:
            logger.warning(f"Async fetch failed, falling back to sync: {e}")
            return fetch_all_wms_sync(endpoints, timeout)
    else:
        return fetch_all_wms_sync(endpoints, timeout)


def parse_and_filter_layers(
    xml_content: Optional[bytes],
    parser_func: Callable[[bytes], List[Dict[str, Any]]],
    filter_func: Optional[Callable[[Dict[str, Any]], bool]] = None,
    endpoint_name: str = "WMS"
) -> List[Dict[str, Any]]:
    """
    Parse WMS XML and apply filtering

    Args:
        xml_content: XML content to parse (None if fetch failed)
        parser_func: Function to parse XML into layer dicts
        filter_func: Optional function to filter layers
        endpoint_name: Name for logging

    Returns:
        List of layer dictionaries
    """
    if xml_content is None:
        logger.warning(f"No content to parse for {endpoint_name}")
        return []

    try:
        layers = parser_func(xml_content)

        if filter_func:
            layers = [l for l in layers if filter_func(l)]

        logger.info(f"Parsed {len(layers)} layers from {endpoint_name}")
        return layers

    except Exception as e:
        logger.error(f"Error parsing {endpoint_name} capabilities: {e}")
        return []


# Convenience function for the common use case
def fetch_emodnet_and_helcom(
    emodnet_url: str,
    helcom_url: str,
    wms_version: str = "1.3.0",
    timeout: int = 10,
    prefer_async: bool = True
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Fetch both EMODnet and HELCOM capabilities concurrently

    Args:
        emodnet_url: EMODnet WMS base URL
        helcom_url: HELCOM WMS base URL
        wms_version: WMS version for capabilities request
        timeout: Request timeout in seconds
        prefer_async: Use async mode if available

    Returns:
        Tuple of (emodnet_layers, helcom_layers) - empty lists on failure
    """
    endpoints = [
        {
            'url': emodnet_url,
            'params': {'service': 'WMS', 'version': wms_version, 'request': 'GetCapabilities'},
            'name': 'EMODnet'
        },
        {
            'url': helcom_url,
            'params': {'service': 'WMS', 'version': wms_version, 'request': 'GetCapabilities'},
            'name': 'HELCOM'
        }
    ]

    results = fetch_all_wms(endpoints, timeout, prefer_async)

    return results[0], results[1]
