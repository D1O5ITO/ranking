from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import json
from collections import defaultdict

import os
TOKEN = os.getenv("TOKEN")
# Ruta del archivo JSON donde se almacenará la participación
PARTICIPATION_FILE = 'participation_data.json'

# Cargar los datos de participación desde el archivo JSON
def load_participation_data():
    if os.path.exists(PARTICIPATION_FILE):
        with open(PARTICIPATION_FILE, 'r') as file:
            data = json.load(file)
            return defaultdict(int, data)
    else:
        return defaultdict(int)

# Guardar los datos de participación en el archivo JSON
def save_participation_data(data):
    with open(PARTICIPATION_FILE, 'w') as file:
        json.dump(data, file)

# Diccionario para almacenar la cantidad de archivos enviados por cada usuario
user_files = load_participation_data()

# Comando /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('¡Hola! Soy tu bot para llevar un ranking de participación.')

# Función para manejar los archivos enviados
def handle_media(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id not in user_files:
        user_files[user_id] = 0
        save_participation_data(user_files)

    if update.message.photo or update.message.video:
        user_files[user_id] += 1
        save_participation_data(user_files)
        update.message.reply_text('¡Archivo recibido! Te contamos como participación 🫲.')

# Función para mostrar el ranking
def show_ranking(update: Update, context: CallbackContext) -> None:
    sorted_users = sorted(user_files.items(), key=lambda x: x[1], reverse=True)

    ranking_message = "🏆 Top 5 de participación:\n"
    for i, (user_id, count) in enumerate(sorted_users[:5], 1):
        try:
            user = context.bot.get_chat_member(update.message.chat_id, user_id)
            user_name = user.user.first_name + " " + (user.user.last_name if user.user.last_name else "")
        except Exception as e:
            user_name = f"Usuario {user_id}"

        ranking_message += f"{i}. {user_name}: {count} archivos enviados\n"

    no_participation = "🙃 Lista de quienes no enviaron nada:\n"
    for user_id in user_files:
        if user_files[user_id] == 0:
            try:
                user = context.bot.get_chat_member(update.message.chat_id, user_id)
                user_name = user.user.first_name + " " + (user.user.last_name if user.user.last_name else "")
            except Exception as e:
                print(f"Error al obtener el nombre del usuario {user_id}: {e}")
                user_name = f"Usuario {user_id}"

            no_participation += f"{user_name}\n"

    update.message.reply_text(ranking_message + no_participation)

# Función para enviar el ranking solo si el usuario es admin o el creador del bot
def send_ranking(update: Update, context: CallbackContext):
    # Verificar si el usuario que ejecuta el comando es admin o tú
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    admins = context.bot.get_chat_administrators(chat_id)
    admin_ids = [admin.user.id for admin in admins]

    # Agrega tu ID aquí
    my_user_id = 123456789  # Reemplaza con tu ID de Telegram

    if user_id not in admin_ids and user_id != my_user_id:
        update.message.reply_text("No tienes permiso para ejecutar este comando.")
        return

    user_files = load_participation_data()
    sorted_users = sorted(user_files.items(), key=lambda x: x[1], reverse=True)

    ranking_message = "📊 Ranking completo de participación 📊 :\n"
    for i, (user_id, count) in enumerate(sorted_users, 1):
        try:
            user = context.bot.get_chat_member(chat_id, int(user_id)).user
            user_name = f"{user.first_name} {user.last_name or ''}".strip()
        except Exception:
            user_name = f"Usuario {user_id}"
        ranking_message += f"{i}. {user_name}: {count} archivos enviados\n"

    no_participation = " ❌ Lista de quienes no enviaron nada ❌:\n"
    for user_id, count in user_files.items():
        if count == 0:
            try:
                user = context.bot.get_chat_member(chat_id, int(user_id)).user
                user_name = f"{user.first_name} {user.last_name or ''}".strip()
            except Exception:
                user_name = f"Usuario {user_id}"
            no_participation += f"{user_name}\n"

    context.bot.send_message(chat_id=chat_id, text=ranking_message + no_participation)

# Función para resetear el ranking
def reset_ranking(update: Update, context: CallbackContext):
    # Verificar si el usuario es admin o el creador
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    admins = context.bot.get_chat_administrators(chat_id)
    admin_ids = [admin.user.id for admin in admins]

    # Agrega tu ID aquí
    my_user_id = 123456789  # Reemplaza con tu ID de Telegram

    if user_id not in admin_ids and user_id != my_user_id:
        update.message.reply_text("No tienes permiso para ejecutar este comando.")
        return

    save_participation_data({})  # Vaciar el archivo JSON
    update.message.reply_text("El ranking ha sido reseteado.")

# Función principal que maneja la actualización del bot
def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Registra los manejadores de comandos
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("ranking", show_ranking))
    dispatcher.add_handler(CommandHandler("send_ranking", send_ranking))
    dispatcher.add_handler(CommandHandler("reset_ranking", reset_ranking))

    # Registra el manejador de archivos (imágenes y videos)
    dispatcher.add_handler(MessageHandler(Filters.photo | Filters.video, handle_media))
    print("El bot está corriendo...")
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
