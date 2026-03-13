pip3 install -r requirements.txt
source venv/bin/activate
nohup python3 main.py &


# Printer Task Server

This project sets up a simple web server on a Raspberry Pi to allow submitting tasks for printing on a thermal receipt printer.

lsusb

## Setup

1.  **Dependencies:** Ensure you have Python 3 and `pip` installed. The required Python packages are listed in `requirements.txt`.
    ```bash
    source venv/bin/activate
    pip3 install -r requirements.txt
    ```

2.  **Hardware:** Make sure your ESC/POS printer is connected and configured correctly for `escpos.printer.Usb` to function.

## Running the Server

To start the web server, navigate to the project directory and run:

```bash
nohup python3 bot.py 
nohup python3 app.py &
```

This command will start the Flask application in the background. The `nohup` command prevents the process from being terminated when you log out of your SSH session, and `&` runs the command in the background.

### Accessing the Server

The server will be accessible on your LAN at `http://192.168.x.x:8333` (replace `192.168.x.x` with your Raspberry Pi's actual IP address).

### Apple Shortcuts Integration

You can send tasks to the printer using Apple Shortcuts by making a POST request to the `/apple-shortcut-task` endpoint.

**Endpoint:** 
8333: 
submit

trigger_thread

**Method:** `POST`

**Content-Type:** `application/json`

**Example Request Body:**
```json
{
  "task": "Remember to buy milk and eggs."
}
```

### More Robust Persistent Execution (Optional - Systemd)

For a more robust and manageable persistent service, especially for production environments, it is recommended to set up a `systemd` service. Here's a basic outline:

1.  **Create a service file** (e.g., `/etc/systemd/system/printer_task.service`):
    ```ini
    [Unit]
    Description=Printer Task Server
    After=network.target

    [Service]
    User=pi  # Replace with your Raspberry Pi username
    WorkingDirectory=/home/pi/printer # Replace with your project directory
    ExecStart=/usr/bin/python3 /home/pi/printer/app.py
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
    *   Adjust `User` and `WorkingDirectory` to match your setup.
    *   Ensure the `ExecStart` path to `python3` and `app.py` is correct.

2.  **Reload systemd and enable the service**:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable printer_task.service
    sudo systemctl start printer_task.service
    ```

3.  **Check status (optional)**:
    ```bash
    sudo systemctl status printer_task.service


     ps aux | grep
     kill

problems to solve: dynamic pdf-html size
