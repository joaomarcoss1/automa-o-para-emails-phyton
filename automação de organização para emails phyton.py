import imaplib
import email
from email.header import decode_header
import getpass

# Configurações do e-mail
EMAIL = input("Digite seu e-mail: ")
PASSWORD = getpass.getpass("Digite sua senha: ")
IMAP_SERVER = "imap.gmail.com"  # Para Gmail (pode mudar para Outlook, etc.)

# Conectar ao servidor IMAP
mail = imaplib.IMAP4_SSL(IMAP_SERVER)

try:
    mail.login(EMAIL, PASSWORD)
    print("Login realizado com sucesso!")
except imaplib.IMAP4.error:
    print("Erro ao fazer login. Verifique seu e-mail/senha ou permissões de IMAP.")
    exit()

# Seleciona a caixa de entrada
mail.select("inbox")

# Buscar todos os e-mails não lidos
status, messages = mail.search(None, 'UNSEEN')
email_ids = messages[0].split()

# Dicionário de regras
regras = {
    "Trabalho": ["@empresa.com", "relatório", "reunião"],
    "Promoções": ["promo", "desconto", "oferta"],
    "Pessoal": ["@familia.com", "aniversário"],
}

# Criar pastas, se necessário
for pasta in regras:
    try:
        mail.create(pasta)
    except:
        pass  # Pasta já existe

# Processar os e-mails
for num in email_ids:
    status, data = mail.fetch(num, '(RFC822)')
    msg = email.message_from_bytes(data[0][1])

    # Decodificar o assunto
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or "utf-8", errors="ignore")

    # Obter remetente
    from_ = msg.get("From")

    # Aplicar regras
    movido = False
    for pasta, palavras in regras.items():
        if any(palavra.lower() in (subject.lower() + from_.lower()) for palavra in palavras):
            mail.copy(num, pasta)
            mail.store(num, '+FLAGS', '\\Deleted')
            movido = True
            print(f"E-mail com assunto '{subject}' movido para a pasta '{pasta}'.")
            break

    if not movido:
        print(f"E-mail com assunto '{subject}' não corresponde a nenhuma regra.")

# Expungir (apagar marcados como deletados)
mail.expunge()

# Encerrar sessão
mail.logout()
print("Organização concluída!")
