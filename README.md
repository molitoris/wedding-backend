# Wedding Backend 🕊️💍
Welcome to the Wedding Backend, the backbone for my wedding website. Built with Python and FastAPI, this API allows to register guest digitally.

## Features 🌟

- **User Registration & Management**: Endpoints to handle user registration, email verification, login, password recovery, and password reset. 📇

- **Guest Management**: Easily manage wedding guest list, from adding guest information to retrieving it, ensuring you have all the details needed for your big day. 🧑‍🤝‍🧑

- **Contact Form**: A dedicated endpoint to handle messages sent through the contact form on your wedding website, including background email sending functionality. 📧

- **Security**: Utilizes HTTP Bearer tokens for authentication, ensuring that user and guest information is protected throughout the planning process. 🔐

## Getting Started
To get started with the Wedding Backend, follow these steps:

1. **Install docker**
1. **Clone the repository** to your local machine or server.
1. **Customize configuration** by adding `config/config.json`
1. **Build docker container** by running `docker build -t wedding-backend .`
1. **Run docker container** by running `docker run --name wedding-backend wedding-backend`


## API Endpoints

### Health Check

- `GET /ping`: Returns `{'message': 'pong'}` to indicate the API is running.

### User Management

- `POST /user-register`: Register a new user.
- `POST /email-verification`: Verify the user's email address.
- `POST /login`: Authenticate a user.
- `POST /forget-password`: Initiate a password reset process.
- `POST /reset-password`: Reset a user's password.

### Guest Management

- `GET /guest-info`: Retrieve information about the guests.
- `POST /guest-info`: Update guest information.

### Contact Form

- `GET /contact_info`: Retrieve contact information.
- `POST /send_message`: Send a message through the contact form.

## Development

To ensure a consistent development environment, a `devcontainer` configuration is provided.

### Run dev mail server
```
python -m smtpd -c DebuggingServer -n localhost:1025
```

## Contribution

Contributions are welcome! If you'd like to improve the Wedding Planner API or add new features, please feel free to fork the repository, make your changes, and submit a pull request.

## Support

If you encounter any issues or have questions, please submit an issue on the GitHub repository.

---

Embrace the journey to your special day with the Wedding Backend. 💒🎉


