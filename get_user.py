from pyrogram import Client

app = Client("get_user", api_id=1698118, api_hash="3c526bc05bfe7c9856fb556b7054bfb3")

async def main(user_id):
    user = await app.get_users(user_id)
    print(user)

if __name__ == "__main__":
    with app:
        user_id = 181777337  # Замените на нужное user_id
        app.run(main(user_id))