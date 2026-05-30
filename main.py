import asyncio
import json
import socket
import struct
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager

KV = """
ScreenManager:
    HomeScreen:

<HomeScreen>:
    name: 'home'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(16)

        Label:
            text: 'MobileSwamp'
            font_size: sp(32)
            bold: True
            size_hint_y: None
            height: dp(70)

        Label:
            id: status
            text: 'Select your role'
            font_size: sp(15)
            color: 0.6, 0.6, 0.6, 1
            size_hint_y: None
            height: dp(40)
            text_size: self.width, None
            halign: 'center'

        Button:
            id: master_btn
            text: 'MASTER'
            size_hint_y: None
            height: dp(60)
            on_press: app.start_master()

        Button:
            id: node_btn
            text: 'NODE'
            size_hint_y: None
            height: dp(60)
            on_press: root.show_ip_input()

        BoxLayout:
            id: ip_row
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(52)
            spacing: dp(8)
            opacity: 0
            disabled: True

            TextInput:
                id: ip_input
                hint_text: "Master IP address"
                multiline: False
                input_type: 'number'

            Button:
                text: 'Connect'
                size_hint_x: None
                width: dp(110)
                on_press: app.start_node(ip_input.text.strip())

        Widget:
"""


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


async def send_msg(writer, msg: dict):
    data = json.dumps(msg).encode()
    writer.write(struct.pack(">I", len(data)) + data)
    await writer.drain()


async def recv_msg(reader) -> dict:
    header = await reader.readexactly(4)
    length = struct.unpack(">I", header)[0]
    body = await reader.readexactly(length)
    return json.loads(body.decode())


class HomeScreen(Screen):
    def show_ip_input(self):
        row = self.ids.ip_row
        row.opacity = 1
        row.disabled = False


class MobileSwampApp(App):
    def build(self):
        self.role = None
        self.device_name = socket.gethostname()
        self.loop = None
        self.peers = {}  # writer -> peer_name (master only)
        return Builder.load_string(KV)

    def _set_status(self, text):
        def _update(dt):
            self.root.get_screen('home').ids.status.text = text
        Clock.schedule_once(_update)

    # ── MASTER ────────────────────────────────────────────────────────────
    def start_master(self):
        self.role = 'master'
        ip = get_local_ip()
        self._set_status(f'Master • IP: {ip}')
        threading.Thread(target=self._run_master, daemon=True).start()

    def _run_master(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._master_serve())

    async def _master_serve(self):
        server = await asyncio.start_server(
            self._on_node_connected, '0.0.0.0', 54321)
        async with server:
            await server.serve_forever()

    async def _on_node_connected(self, reader, writer):
        peer = writer.get_extra_info('peername')
        try:
            await send_msg(writer, {
                'type': 'hello',
                'name': self.device_name,
                'role': 'master',
            })
            hello = await recv_msg(reader)
            node_name = hello.get('name', str(peer))
            self.peers[writer] = node_name
            self._set_status(f'Connected to {node_name}')
            while True:
                msg = await recv_msg(reader)
                # relay to other nodes in future phases
        except Exception:
            pass
        finally:
            self.peers.pop(writer, None)
            writer.close()
            self._set_status(f'Node disconnected • {get_local_ip()}')

    # ── NODE ──────────────────────────────────────────────────────────────
    def start_node(self, master_ip):
        if not master_ip:
            self._set_status('Enter master IP first')
            return
        self.role = 'node'
        self._set_status(f'Connecting to {master_ip}…')
        threading.Thread(
            target=self._run_node, args=(master_ip,), daemon=True).start()

    def _run_node(self, master_ip):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._node_connect(master_ip))

    async def _node_connect(self, master_ip):
        try:
            reader, writer = await asyncio.open_connection(master_ip, 54321)
            await send_msg(writer, {
                'type': 'hello',
                'name': self.device_name,
                'role': 'node',
            })
            hello = await recv_msg(reader)
            master_name = hello.get('name', master_ip)
            self._set_status(f'Connected to {master_name}')
            while True:
                msg = await recv_msg(reader)
        except Exception as e:
            self._set_status(f'Connection failed: {e}')


if __name__ == '__main__':
    MobileSwampApp().run()
