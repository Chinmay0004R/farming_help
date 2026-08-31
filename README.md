# Farm Management

A Django-based farm management application for recording farms, plots, crops, harvests, finances, field notes, reminders, and IoT sensor readings. The interface is designed for day-to-day farm work, with Marathi labels in the main dashboard.

## Current Status

The project is a working MVP. The following features are implemented:

- Farmer registration, login, logout, and profile updates
- Multiple farms per farmer, including location and total area
- Plot management with area, soil type, and irrigation type
- Personal crop catalog with variety and expected yield information
- Crop cycles with season, sowing and harvest dates, growth stage, expected yield, and notes
- Harvest records with quantity, quality, moisture, labour cost, and transport cost
- Automatic crop-cycle actual yield totals from harvest records
- Expense and sale tracking with total expense, sales, and profit calculations
- Farming diary for dated field notes
- Reminders that can be marked as completed
- Farmer dashboard with farm and crop summaries
- Soil-moisture status: dry fields are flagged when moisture is below 30%
- High-temperature and missing-sensor alerts on the dashboard
- Five-day weather forecasts, rainfall totals, and weather-aware irrigation or spraying alerts
- IoT device registration and ownership-based access control
- ESP32 sensor API for soil moisture, temperature, humidity, and battery voltage
- Plot sensor history displayed on the plot detail page
- Marathi, Hindi, and English language selector for the shared navigation
- Django admin panel

All farmer-facing records are restricted to the authenticated owner. The application currently uses SQLite for local development.

## Technology

- Python
- Django
- SQLite
- HTML templates and CSS
- ESP32/Arduino-compatible sensor integration through a JSON HTTP endpoint

## Requirements

- Python 3.10 or newer
- `pip`
- Optional: an ESP32 device and sensors for IoT features

## Installation

Open PowerShell in the project directory:

```powershell
cd E:\farm_management\farm_management
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install Django
python manage.py migrate
```

If PowerShell blocks activation, run this once for the current user or activate the environment from another shell:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Run the Application

```powershell
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in a browser. Create an account at `/accounts/register/`, then add a farm, plot, crop, and crop cycle.

Useful URLs:

| URL | Purpose |
| --- | --- |
| `/` | Farmer dashboard |
| `/accounts/register/` | Create an account |
| `/accounts/login/` | Sign in |
| `/accounts/profile/` | Update profile |
| `/farms/` | View and manage farms |
| `/farms/money/` | Record expenses and sales |
| `/farms/diary/` | Add farming diary entries |
| `/farms/reminders/` | Add and complete reminders |
| `/crops/catalog/` | Manage the crop catalog |
| `/crops/cycles/` | Manage crop cycles and harvests |
| `/iot/devices/` | Register and manage IoT devices |
| `/admin/` | Django administration |

## Create an Admin User

```powershell
python manage.py createsuperuser
```

Then visit <http://127.0.0.1:8000/admin/>.

## ESP32 Sensor API

1. Create a plot from the application.
2. Register a device at `/iot/devices/` and assign it to the plot.
3. Copy the generated device key and API URL from the device detail page.
4. Configure the Wi-Fi credentials and endpoint in the generated Arduino sketch.

Send a `POST` request to `/iot/readings/` with the device key in the `X-Device-Key` header:

```http
POST /iot/readings/ HTTP/1.1
Content-Type: application/json
X-Device-Key: YOUR_DEVICE_KEY

{
	"soil_moisture": 42.5,
	"temperature": 25.1,
	"humidity": 61.0,
	"battery_voltage": 4.1
}
```

The API returns HTTP `201` when the reading is accepted. `recorded_at` is optional; if omitted, the server uses the current time.

## Development Checks

```powershell
python manage.py check
python manage.py test
python manage.py makemigrations
python manage.py migrate
```

Do not run `makemigrations` unless you have intentionally changed a model. Commit migration files when model changes are part of a feature.

## Project Structure

```text
accounts/       Authentication and farmer profiles
farms/          Farms, expenses, sales, diary entries, reminders, dashboard
plots/          Farm plots and sensor-history views
crops/          Crop catalog, crop cycles, and harvests
iot/            Devices, sensor readings, and ESP32 API
farm_management/ Django settings and root URLs
templates/      HTML templates
static/         CSS assets
db.sqlite3       Local development database
```

## Planned Future Upgrades

The next upgrades should focus on useful decisions for farmers rather than exposing more technical data:

1. Improve sensor processing with configurable moisture thresholds, stale-device detection, and clearer watering recommendations.
3. Expand translations across every form, validation message, and page.
4. Add simple seasonal profitability views, crop-wise expense allocation, and downloadable PDF or Excel reports.
5. Add input inventory for seeds, fertilizer, and chemicals with low-stock and expiry alerts.
6. Add irrigation history, water usage, and optional pump monitoring.
7. Add labour and machinery records only after the core farm workflow is stable.
8. Add plot GPS boundaries and maps.
9. Add production deployment support: environment-based secrets, PostgreSQL, HTTPS, secure API authentication, backups, logging, and automated tests.
10. Add mobile/PWA and offline data entry for farms with unreliable connectivity.

Advanced AI assistance, market prediction, and automated irrigation should come after reliable data collection and reporting are established.

## Production Notes

The current settings are intended for local development: `DEBUG` is enabled, SQLite is used, and the secret key is stored in settings. Before deployment, move secrets to environment variables, set `DEBUG = False`, configure `ALLOWED_HOSTS`, use a production database, enable HTTPS, and review the IoT API security model.
