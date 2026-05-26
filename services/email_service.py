import os
import resend

# A chave da API será puxada das variáveis do Railway
resend.api_key = os.getenv("RESEND_API_KEY")

def send_email(to_email: str, employee_name: str, card_path: str):
    
    print("1 - Iniciando envio via Resend")

    try:
        # Lê o arquivo de imagem do cartão gerado
        with open(card_path, "rb") as image_file:
            image_data = image_file.read()
            
        print("2 - Imagem carregada com sucesso")

        # Monta a estrutura do e-mail
        params = {
            "from": "Sua Empresa <onboarding@resend.dev>", 
            "to": [to_email],
            "subject": "Feliz Aniversário! 🎉",
            "html": f"<p>Prezado(a) <strong>{employee_name}</strong>,</p><p>Desejamos a você um excelente feliz aniversário!</p>",
            "attachments": [
                {
                    "filename": f"{employee_name}.png",
                    # O SDK do Resend exige que os bytes do arquivo sejam passados como uma lista
                    "content": list(image_data) 
                }
            ]
        }

        print("3 - Enviando requisição para a API...")
        
        email_response = resend.Emails.send(params)
        
        print(f"4 - Sucesso! ID do E-mail: {email_response.get('id')}")

    except Exception as error:
        print("ERRO NO ENVIO DE E-MAIL:")
        print(error)
        raise error