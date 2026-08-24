import base64
import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")


def send_email(to_email: str, employee_name: str, card_path: str):
    print("1 - Iniciando envio via Resend")

    try:
        with open(card_path, "rb") as image_file:
            image_data = image_file.read()
            # Converte os bytes para string Base64 exigida pela API
            encoded_content = base64.b64encode(image_data).decode("utf-8")

        print("2 - Imagem carregada e convertida com sucesso")

        params = {
            "from": "Secretaria de Saúde <onboarding@resend.dev>",
            "to": [to_email],
            "subject": "Feliz Aniversário! 🎉",
            "html": f"<p>Prezado(a) <strong>{employee_name}</strong>,</p><p>A Secretaria Municipal de Saúde deseja a você um excelente aniversário!</p>",
            "attachments": [
                {
                    "filename": f"{employee_name}.png",
                    "content": encoded_content,
                }
            ],
        }

        print("3 - Enviando requisição para a API...")
        email_response = resend.Emails.send(params)
        print(f"4 - Sucesso! ID do E-mail: {email_response.get('id')}")

        return email_response

    except Exception as error:
        print(f"ERRO NO ENVIO DE E-MAIL: {error}")
        raise error