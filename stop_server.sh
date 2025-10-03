#!/bin/bash
# MARBEFES BBT Database - Server Stop Script
# This script stops any running Flask servers

echo "🛑 MARBEFES BBT Database - Stopping Flask Servers"
echo "================================================="

# Find all processes running app.py or run_flask.py
flask_pids=$(pgrep -f "python.*app\.py\|python.*run_flask\.py" 2>/dev/null || true)

if [ -z "$flask_pids" ]; then
    echo "✅ No Flask servers found running"
else
    echo "🔍 Found Flask servers running:"
    for pid in $flask_pids; do
        echo "   PID: $pid"
        ps -p $pid -o pid,ppid,cmd --no-headers 2>/dev/null || true
    done

    echo ""
    echo "🛑 Stopping Flask servers..."
    for pid in $flask_pids; do
        if kill -TERM $pid 2>/dev/null; then
            echo "   ✅ Stopped server with PID: $pid"
        else
            echo "   ⚠️  Could not stop server with PID: $pid"
        fi
    done

    # Wait a moment for graceful shutdown
    sleep 2

    # Check for any remaining processes and force kill if necessary
    remaining_pids=$(pgrep -f "python.*app\.py\|python.*run_flask\.py" 2>/dev/null || true)
    if [ ! -z "$remaining_pids" ]; then
        echo "⚠️  Some processes still running, force killing..."
        for pid in $remaining_pids; do
            if kill -KILL $pid 2>/dev/null; then
                echo "   🔨 Force killed PID: $pid"
            fi
        done
    fi
fi

# Also check for any processes listening on common Flask ports
echo ""
echo "🔍 Checking for processes on common Flask ports..."
for port in 5000 5001 8000 8080; do
    pid=$(lsof -ti :$port 2>/dev/null || true)
    if [ ! -z "$pid" ]; then
        echo "   ⚠️  Process $pid is using port $port"
        echo "   Run 'sudo kill $pid' to stop it if needed"
    fi
done

echo ""
echo "✅ Server stop script completed"
echo "💡 To start the server again, run: ./start_server.sh"