
# AWS Infrastructure Monitoring API

A **Flask-based monitoring solution** that provides real-time insights into your AWS infrastructure. This application helps DevOps teams and security engineers monitor critical AWS services like ECS, S3, EBS, and VPC configurations through RESTful APIs.

---

##  Features

- **Real-time Monitoring** of AWS resources
- **Multi-service Support**: ECS, S3, EBS, Network
- **Session-based Authentication** using temporary AWS credentials
- **Secure Memory Management**: AWS credentials are stored only in-memory and cleared upon expiration
- **Extensible Flask Structure** for modular expansion

---

##  Supported AWS Services

| Service | Features |
|--------|----------|
| **Amazon ECS** | List and describe clusters, services, task status |
| **Amazon S3** | List buckets, get properties |

---

##  Project Structure

```
.
├── app.py                # Main Flask app
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── (Future) /api/v1/     # API modules per service
```

---

##  Authentication Flow

**POST** `/api/v1/auth/login`  
Accepts temporary AWS credentials and creates a session.

### Request:
```json
{
  "aws_access_key_id": "<your-access-key>",
  "aws_secret_access_key": "<your-secret-key>",
  "aws_region": "us-west-2"
}
```

### Response:
```json
{
  "expires_at": "2025-03-06T14:30:00Z"
}
```

>  Session expires after 5 minutes. Credentials are cleared every 60 seconds in the background.

---

##  API Endpoints

###  ECS Monitoring

**GET** `/api/v1/ecs/clusters`  
Returns cluster info including status, task counts, and service counts.

---

###  S3 Monitoring

**GET** `/api/v1/s3/buckets`  
Returns a list of all accessible S3 buckets.

---

##  Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/your-repo/aws-monitoring-app.git
cd aws-monitoring-app
```

2. **Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the app**
```bash
python app.py
```

---

## Submits:
- Maor Ryngler
- Amit Tal Levi 
