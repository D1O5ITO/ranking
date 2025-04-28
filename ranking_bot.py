from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import json
from collections import defaultdict
import os

TOKEN = os.getenv("TOKEN")

PARTICIPATION_FILE = 'participation_data.json'

# ✅ Cargar participación
def load_participation_data():
    if os.path.exists(PARTICIPATION_FILE):
        with open(PARTICIPATION_FILE, 'r') as file:
            data = json.load(file)
            return defaultdict(int, {int(k): v for k, v in data.items()})
    else:
        return defaultdict(int)

# ✅ Guardar participación
def save_participation_data(data):
    with open(PARTICIPATION_FILE, 'w') as file:
        json.dump(data, file)

# ✅ Diccionario interno de participación
user_files = load_participation_data()

# ✅ Tu ID personal de Telegram (REEMPLAZA ESTE POR EL TUYO)
MY_USER_ID = 5804784715  

# ✅ Comando /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text('¡Hola! Soy tu bot para llevar un ranking de participación.')

# ✅ Manejador de imágenes y videos
def handle_media(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id not in user_files:
        user_files[user_id] = 0

    if update.message.photo or update.message.video:
        user_files[user_id] += 1
        update.message.reply_text('¡Archivo recibido! Te contamos como participación 🫲.')

# ✅ Verificación de Admin
def is_admin(update: Update):
    return update.message.from_user.id == MY_USER_ID

# ✅ /send_ranking — mostrar lo de memoria
def send_ranking(update: Update, context: CallbackContext):
    if not is_admin(update):
        update.message.reply_text("No tienes permiso para usar este comando.")
        return

    sorted_users = sorted(user_files.items(), key=lambda x: x[1], reverse=True)

    message = "📊 Ranking Actual (Memoria Temporal):\n"
    for i, (user_id, count) in enumerate(sorted_users, 1):
        try:
            user = context.bot.get_chat_member(update.message.chat_id, user_id).user
            user_name = f"{user.first_name} {user.last_name or ''}".strip()
        except Exception:
            user_name = f"Usuario {user_id}"
        message += f"{i}. {user_name}: {count} archivos enviados\n"

    update.message.reply_text(message)

# ✅ /siempre_ranking — mostrar lo del archivo JSON
def siempre_ranking(update: Update, context: CallbackContext):
    if not is_admin(update):
        update.message.reply_text("No tienes permiso para usar este comando.")
        return

    participation_data = load_participation_data()
    sorted_users = sorted(participation_data.items(), key=lambda x: x[1], reverse=True)

    message = "📂 Ranking Histórico :\n"
    for i, (user_id, count) in enumerate(sorted_users, 1):
        try:
            user = context.bot.get_chat_member(update.message.chat_id, user_id).user
            user_name = f"{user.first_name} {user.last_name or ''}".strip()
        except Exception:
            user_name = f"Usuario {user_id}"
        message += f"{i}. {user_name}: {count} archivos enviados\n"

    update.message.reply_text(message)

# ✅ /reset_ranking — guardar lo interno al archivo y resetear
def reset_ranking(update: Update, context: CallbackContext):
    if not is_admin(update):
        update.message.reply_text("No tienes permiso para usar este comando.")
        return

    participation_data = load_participation_data()

    # Sumar lo que está en memoria
    for user_id, count in user_files.items():
        participation_data[user_id] = participation_data.get(user_id, 0) + count

    save_participation_data(participation_data)  # Guardar el nuevo estado

    user_files.clear()  # Limpiar la memoria interna

    update.message.reply_text("✅ Datos guardados en el historial y participación semanal reseteada.")

# ✅ Función principal
def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("send_ranking", send_ranking))
    dispatcher.add_handler(CommandHandler("siempre_ranking", siempre_ranking))
    dispatcher.add_handler(CommandHandler("reset_ranking", reset_ranking))
    dispatcher.add_handler(MessageHandler(Filters.photo | Filters.video, handle_media))

    print("El bot está corriendo...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
