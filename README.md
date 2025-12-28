# MARBEFES BBT Database - Refactored Version

## Overview
This is a refactored version of the MARBEFES BBT Database application, transformed from a monolithic 2,500+ line file into a modular, maintainable, and secure Flask application following best practices.

## Key Improvements

### 🏗️ Architecture
- **Modular Structure**: Separated into blueprints, services, and utilities
- **Configuration Management**: Environment-based configuration
- **Service Layer**: Business logic separated from routes
- **Clean Separation**: HTML/CSS/JS separated from Python code

### 🔒 Security Enhancements
- Input validation on all user inputs
- SQL injection prevention
- XSS protection
- CORS properly configured
- Rate limiting support
- Secure session handling

### ⚡ Performance Improvements
- Caching layer implementation
- Connection pooling
- Lazy loading of resources
- Optimized database queries
- Response compression support

### 🧪 Testing & Quality
- Unit test structure
- Code coverage support
- Type hints throughout
- Comprehensive error handling
- Logging framework

## Project Structure
```
refactored_marbefes/
├── app.py                    # Application factory and entry point
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── blueprints/              
│   ├── __init__.py
│   ├── main.py              # Main web routes
│   ├── api.py               # RESTful API endpoints
│   └── vector.py            # Vector data endpoints
├── services/
│   ├── __init__.py
│   ├── wms_service.py       # WMS operations service
│   ├── vector_service.py    # Vector data service
│   └── layer_service.py     # Layer management service
├── utils/
│   ├── __init__.py
│   ├── validators.py        # Input validation
│   ├── cache.py            # Caching utilities
│   └── security.py         # Security utilities
├── static/
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript modules
│   └── img/                # Images and logos
├── templates/              # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   └── test.html
└── tests/                  # Test suite
    ├── test_api.py
    └── test_services.py
```

## Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd refactored_marbefes
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set environment variables**
```bash
# Create .env file
cat > .env << EOF
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
WMS_BASE_URL=https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms
HELCOM_WMS_BASE_URL=https://maps.helcom.fi/arcgis/services/MADS/Pressures/MapServer/WMSServer
EOF
```

5. **Run the application**
```bash
python app.py
```

## Configuration

The application supports three environments:
- **development**: Debug mode enabled, simple cache
- **production**: Optimized settings, Redis cache
- **testing**: Testing configuration

Set via environment variable:
```bash
export FLASK_ENV=production
```

## API Endpoints

### Core Endpoints
- `GET /` - Main map interface
- `GET /health` - Health check

### API Endpoints
- `GET /api/layers` - Get WMS layers
- `GET /api/helcom-layers` - Get HELCOM layers
- `GET /api/all-layers` - Get all available layers
- `GET /api/capabilities` - WMS capabilities
- `GET /api/legend/<layer>` - Layer legend URL
- `POST /api/feature-info` - Get feature information

### Vector Endpoints
- `GET /api/vector/layers` - List vector layers
- `GET /api/vector/layer/<name>` - Get layer GeoJSON
- `GET /api/vector/bounds` - Get layer bounds

## Development

### Running Tests
```bash
pytest
pytest --cov=.  # With coverage
```

### Code Quality
```bash
black .  # Format code
flake8   # Lint code
mypy .   # Type checking
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

## Production Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### With Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /static {
        alias /path/to/refactored_marbefes/static;
    }
}
```

## Monitoring

### Logging
Logs are written to `logs/marbefes.log` with rotation.

### Metrics
Optional Prometheus metrics available at `/metrics` endpoint.

### Cache Statistics
```python
from utils.cache import get_cache
stats = get_cache().get_stats()
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` file
2. **Secret Key**: Use strong random key in production
3. **HTTPS**: Always use HTTPS in production
4. **Rate Limiting**: Configure appropriate limits
5. **CORS**: Restrict origins in production
6. **Input Validation**: All inputs are validated

## Performance Optimization

1. **Caching**: Configure Redis for production
2. **Database**: Use PostgreSQL with PostGIS
3. **CDN**: Serve static files via CDN
4. **Compression**: Enable gzip compression
5. **Load Balancing**: Use multiple workers

## Troubleshooting

### Vector Support Not Working
```bash
pip install geopandas fiona pyproj shapely
```

### Redis Connection Error
```bash
# Check Redis is running
redis-cli ping
```

### Permission Errors
```bash
# Ensure log directory exists
mkdir -p logs
chmod 755 logs
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit pull request

## License

This project is part of the MARBEFES project funded by Horizon Europe Grant Agreement No. 101060937.

## Support

For issues or questions:
- GitHub Issues: [Create an issue]
- Documentation: [MARBEFES website](https://marbefes.eu)
- Email: support@marbefes.eu

## Migration from Original

To migrate from the original monolithic application:

1. **Backup existing data**
2. **Update configuration** to match new structure
3. **Test in development** environment first
4. **Deploy gradually** using blue-green deployment
5. **Monitor logs** for any issues

## Credits

- Original application by MARBEFES team
- Refactored by: [Your Name]
- Date: 2024

---

**Note**: This refactored version maintains full compatibility with the original application while providing significant improvements in maintainability, security, and performance.
