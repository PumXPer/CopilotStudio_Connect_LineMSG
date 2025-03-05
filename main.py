import time
from fastapi import FastAPI, Request
from copilot_api import CopilotAPI
from line_bot import LineBot
import asyncio

app = FastAPI()
copilot = CopilotAPI()
line_bot = LineBot()

@app.get("/")
def read_root():
    return {"Hello": "World"}

async def wait_for_bot_response(copilot, token, conversation_id, timeout=30, interval=2):
    """
    รอจนกว่าจะได้รับข้อความจากบอท หรือจนกว่าจะหมดเวลา timeout
    """
    start_time = time.perf_counter()  # เริ่มจับเวลา
    elapsed_time = 0
    
    while elapsed_time < timeout:
        res = copilot.get_messages(token, conversation_id)
        print("📩 Full response from API:", res)

        activities = res.get("activities", [])
        bot_messages = [msg for msg in activities if isinstance(msg, dict) and msg.get("from", {}).get("id", "") != "user1"]
        
        if bot_messages:
            end_time = time.perf_counter()  # จับเวลาสิ้นสุด
            print(f"✅ Bot ตอบกลับภายใน {end_time - start_time:.2f} วินาที")
            return bot_messages  # ส่งคืนข้อความจากบอททันทีที่ได้รับ
        
        await asyncio.sleep(interval)  # รอ interval วินาที ก่อนตรวจสอบอีกครั้ง
        elapsed_time += interval

    print("⏳ หมดเวลารอการตอบกลับจากบอท")
    return []  # ถ้าหมดเวลา ให้คืนค่าเป็น list ว่าง

@app.post("/webhook")
async def webhook(request: Request):
    try:
        total_start = time.perf_counter()  # ⏱ เริ่มจับเวลาทั้งหมด
        body = await request.json()
        print("📩 ข้อความจาก LINE Messaging API:", body)

        events = body.get("events", [])

        for event in events:
            if event.get("type") == "message" and event["message"].get("type") == "text":
                process_start = time.perf_counter()  # ⏱ เริ่มจับเวลาของแต่ละ process
                
                user_msg = event["message"]["text"]
                reply_token = event["replyToken"]

                # ⏱ จับเวลาขอ Token
                token_start = time.perf_counter()
                token = copilot.get_token()
                token_end = time.perf_counter()
                print(f"🔑 ได้รับ Token ใช้เวลา {token_end - token_start:.2f} วินาที")

                if not token:
                    print("ไม่สามารถรับ token ได้")
                    line_bot.reply_message(reply_token, "ขออภัย ระบบขัดข้อง")
                    return {"error": "ไม่สามารถรับ token ได้"}
                
                # ⏱ จับเวลาเริ่มต้น Conversation
                conversation_start = time.perf_counter()
                conversation_id = copilot.start_conversation(token)
                conversation_end = time.perf_counter()
                print(f"💬 เริ่ม Conversation ใช้เวลา {conversation_end - conversation_start:.2f} วินาที")

                if not conversation_id:
                    print("ไม่สามารถเริ่ม conversation ได้")
                    line_bot.reply_message(reply_token, "ขออภัย ระบบขัดข้อง")
                    return {"error": "ไม่สามารถเริ่ม conversation ได้"}
                
                # ⏱ จับเวลาส่งข้อความไปยัง Copilot
                send_start = time.perf_counter()
                send_result = copilot.send_message(token, conversation_id, user_msg)
                send_end = time.perf_counter()
                print(f"📤 ส่งข้อความไปยัง Copilot ใช้เวลา {send_end - send_start:.2f} วินาที")

                # ✅ ใช้ฟังก์ชันรอข้อความจากบอท พร้อมจับเวลา
                bot_messages = await wait_for_bot_response(copilot, token, conversation_id)

                # ⏱ จับเวลาเลือกข้อความตอบกลับ
                select_reply_start = time.perf_counter()
                reply_text = bot_messages[-1].get("text", "") if bot_messages else "ขออภัย ระบบขัดข้อง"
                select_reply_end = time.perf_counter()
                print(f"✏️ เลือกข้อความตอบกลับ ใช้เวลา {select_reply_end - select_reply_start:.2f} วินาที")

                # ⏱ จับเวลาส่งข้อความตอบกลับ LINE
                reply_start = time.perf_counter()
                if send_result and bot_messages:
                    line_bot.reply_message(reply_token, reply_text)
                else:
                    line_bot.reply_message(reply_token, "ขออภัย ระบบขัดข้อง")
                reply_end = time.perf_counter()
                print(f"📩 ส่งข้อความกลับไปยัง LINE ใช้เวลา {reply_end - reply_start:.2f} วินาที")

                process_end = time.perf_counter()
                print(f"✅ กระบวนการทั้งหมดของข้อความนี้ใช้เวลา {process_end - process_start:.2f} วินาที")

        total_end = time.perf_counter()
        print(f"🚀 Webhook process ทั้งหมดใช้เวลา {total_end - total_start:.2f} วินาที")

    except Exception as e:
        print("❌ พบข้อผิดพลาด:", e)
        return {"error": "พบข้อผิดพลาด"}

    return {"status": "success"}
