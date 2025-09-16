import telegram
import asyncio
import json
TOKEN=""
async def connectionbot():
    """
    1) Crée le bot
    2) Récupère un lot d'updates (une seule fois dans cette brique 1)
    3) Envoie "ALERTE DNS CHANGEMENT" une seule fois par chat (anti-doublon via set)
    4) Sauvegarde les updates en JSON lisible (debug/inspection)
    """
    bot = telegram.Bot(TOKEN)

    # Important si, à un moment, tu as configuré un webhook : sans ça, get_updates peut rester vide.
    await bot.delete_webhook()

    # On lit une seule "fournée" d'updates (brique 1 = pas de boucle continue)
    updates = await bot.get_updates(timeout=10)

    # Ensemble des chats déjà notifiés pendant CE run (empêche d'envoyer 2x au même chat)
    seen_run = set()

    # On traite chaque update reçu
    for u in updates:
        # Selon le type d'update, le message peut être dans message / channel_post / edited_*
        msg = u.message or u.channel_post or u.edited_message or u.edited_channel_post
        if not msg:
            continue  # rien à traiter (ex: callback sans message)

        # Texte reçu (peut être None si photo/sticker, d'où le fallback "")
        text = (msg.text or "").strip()

        # Identifiant unique du chat (DM, groupe, canal) — fiable pour dé-duplication
        chat_id = msg.chat.id

        # Règle: on répond uniquement à "/start" et une seule fois par chat_id dans CE run
        if text == "/start" and chat_id not in seen_run:
            try:
                await bot.send_message(chat_id=chat_id, text="ALERTE DNS CHANGEMENT")
                # On marque ce chat comme déjà notifié pour ce run
                seen_run.add(chat_id)
            except Exception:
                # On ne log pas pour rester "propre" comme demandé ; à décommenter si besoin de debug
                # print(f"[WARN] envoi échoué vers {chat_id}: {e}")
                pass

    # Facultatif mais utile: on "accuse réception" des updates lus pour éviter de les revoir au prochain appel
    if updates:
        last_id = updates[-1].update_id
        await bot.get_updates(offset=last_id + 1)

    # Dump JSON des updates pour inspection (encodage UTF-8 pour éviter l’erreur CP1252 sous Windows)
    as_dicts = [u.to_dict() for u in updates]
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(as_dicts, f, ensure_ascii=False, indent=2, default=str)


async def compter():
    """
    Petite tâche parallèle (placeholder) pour montrer la concurrence "async".
    Ici on ne spam pas la console : on se contente d'attendre 10 fois 0.1s.
    """
    for _ in range(10):
        await asyncio.sleep(0.1)


async def main():
    """
    Lance en parallèle:
    - connectionbot() : lit un lot d'updates et notifie une fois par chat "/start"
    - compter()       : simple coroutine qui cède la main (exemple)
    Puis attend que les deux se terminent.
    """
    task1 = asyncio.create_task(connectionbot())
    task2 = asyncio.create_task(compter())
    await asyncio.gather(task1, task2)


if __name__ == "__main__":
    # Point d’entrée : crée/ferme proprement l’event loop et exécute main()
    asyncio.run(main())
