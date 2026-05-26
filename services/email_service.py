import smtplib

from email.mime.multipart import (
    MIMEMultipart
)

from email.mime.text import MIMEText

from email.mime.base import MIMEBase

from email import encoders


EMAIL = "flavintl4@gmail.com"
PASSWORD = "njbd vkub csnr spee"


def send_email(
    to_email: str,
    employee_name: str,
    card_path: str
):

    print("1 - starting")

    message = MIMEMultipart()

    print("2 - message created")

    message["From"] = EMAIL
    message["To"] = to_email
    message["Subject"] = (
        "Feliz Aniversário"
    )

    body = f"""
    Prezado(a) {employee_name},

    Feliz aniversário.
    """

    message.attach(
        MIMEText(body, "plain")
    )

    print("3 - body attached")

    with open(card_path, "rb") as attachment:

        print("4 - opening image")

        part = MIMEBase(
            "application",
            "octet-stream"
        )

        part.set_payload(
            attachment.read()
        )

    print("5 - image loaded")

    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename={employee_name}.png"
    )

    message.attach(part)

    print("6 - attachment added")

    try:

        print("7 - connecting smtp")

        server = smtplib.SMTP(
            "smtp.gmail.com",
            587,
            timeout=10
        )

        print("8 - starttls")

        server.starttls()

        print("9 - login")

        server.login(
            EMAIL,
            PASSWORD
        )

        print("10 - sending")

        server.send_message(message)

        print("11 - success")

        server.quit()

    except Exception as error:

        print("EMAIL ERROR:")
        print(error)

        raise error