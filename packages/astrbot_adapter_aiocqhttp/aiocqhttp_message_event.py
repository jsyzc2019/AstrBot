import os, traceback

from astrbot.api import AstrMessageEvent, MessageChain, logger
from astrbot.api import Plain, Image
from aiocqhttp import CQHttp
from astrbot.core.utils.io import file_to_base64, download_image_by_url

class AiocqhttpMessageEvent(AstrMessageEvent):
    def __init__(self, message_str, message_obj, platform_meta, session_id, bot: CQHttp):
        super().__init__(message_str, message_obj, platform_meta, session_id)
        self.bot = bot
    
    @staticmethod
    async def _parse_onebot_josn(message_chain: MessageChain):
        '''解析成 OneBot json 格式'''
        ret = []
        for segment in message_chain.chain:
            d = segment.toDict()
            if isinstance(segment, Plain):
                d['type'] = 'text'
            if isinstance(segment, Image):
                # convert to base64
                if segment.file and segment.file.startswith("file:///"):
                    image_base64 = file_to_base64(segment.file[8:])
                    image_file_path = segment.file[8:]
                elif segment.file and segment.file.startswith("http"):
                    image_file_path = await download_image_by_url(segment.file)
                    image_base64 = file_to_base64(image_file_path)
                d['data']['file'] = image_base64
            ret.append(d)
        return ret

    async def send(self, message: MessageChain):
        ret = await AiocqhttpMessageEvent._parse_onebot_josn(message)
        if os.environ.get('TEST_MODE', 'off') == 'on':
            return
        await self.bot.send(self.message_obj.raw_message, ret)
        await super().send(message)