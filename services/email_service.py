import base64
import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")


def send_email(
    to_email: str,
    employee_name: str,
    card_path: str
):

    print("1 - Iniciando envio via Resend")

    try:

        first_name = employee_name.split()[0]

        with open(card_path, "rb") as image_file:

            image_data = image_file.read()

            encoded_card = base64.b64encode(
                image_data
            ).decode("utf-8")

        with open(
            "assets/logo_secretaria.png",
            "rb"
        ) as logo_file:

            logo_data = logo_file.read()

            encoded_logo = base64.b64encode(
                logo_data
            ).decode("utf-8")

        print("2 - Imagens carregadas com sucesso")

        params = {

            "from": (
                "Aniversários "
                "<aniversarios@mail.vfilgueiras.cloud>"
            ),

            "to": [to_email],

            "subject": (
                f"Feliz aniversário, {first_name}! 🎉"
            ),

            "html": f"""
                <div style="
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 0 auto;
                    color: #333333;
                    line-height: 1.6;
                ">

                    <p>
                        Olá,
                        <strong>{first_name}</strong>! 🎉
                    </p>

                    <p>
                        Hoje é um dia especial, e não poderíamos
                        deixar de desejar a você um feliz aniversário!
                    </p>

                    <p>
                        Que este novo ciclo seja repleto de
                        saúde, felicidade, boas conquistas
                        e muitos momentos especiais.
                    </p>

                    <p>
                        Esperamos que você aproveite
                        muito o seu dia. 💙
                    </p>

                    <p>
                        Secretaria Municipal de Saúde
                    </p>


                    <!-- ===================================== -->
                    <!-- CARD DE ANIVERSÁRIO -->
                    <!-- ===================================== -->

                    <img
                        src="cid:birthday-card"
                        alt="Cartão de aniversário"
                        style="
                            width: 100%;
                            max-width: 600px;
                            height: auto;
                            display: block;
                            margin: 24px auto 18px auto;
                            border-radius: 12px;
                        "
                    >


                    <!-- ===================================== -->
                    <!-- LOGO DA PREFEITURA / SECRETARIA -->
                    <!-- ===================================== -->
                    <br>

                    <img
                        src="cid:logo-secretaria"
                        alt="Secretaria Municipal de Saúde"
                        style="
                            width: 240px;
                            max-width: 60%;
                            height: auto;
                            display: block;
                            margin: 20px 0 0 0;
                        "
                    >

                </div>
            """,
            
            "attachments": [

                # Card
                {
                    "filename": "cartao_aniversario.png",
                    "content": encoded_card,
                    "content_id": "birthday-card",
                    "content_type": "image/png",
                },

                # Logo
                {
                    "filename": "logo_secretaria.png",
                    "content": encoded_logo,
                    "content_id": "logo-secretaria",
                    "content_type": "image/png",
                }

            ],

        }

        print("3 - Enviando requisição para a API...")

        email_response = resend.Emails.send(params)

        print(
            "4 - Sucesso! ID do E-mail: "
            f"{email_response.get('id')}"
        )

        return email_response

    except Exception as error:

        print(
            f"ERRO NO ENVIO DE E-MAIL: {error}"
        )

        raise error
