import hashlib
import time

ALL_USER_DIC = {}


class Session:
    def __init__(self, handler):
        self.handler = handler
        self.random_index_str = None

    def __get_random_str(self):
        # 生成md5对象
        md = hashlib.md5()

        # 加入自定义参数来更新md5对象
        md.update(bytes(str(time.time()) + ' | own-secret', encoding='utf-8'))

        # 得到加盐后的十六进制随机字符串来作为用户的索引
        return md.hexdigest()

    def __setitem__(self, key, value):
        # 当前session对象中没有对应的索引的时候
        if not self.random_index_str:
            # 根据处理器对象获得浏览器传来的cookie的值
            random_index_str = self.handler.get_secure_cookie("__sson__", None)

            # 浏览器传来的cookie的值为空的时候, 表示该用户是第一次访问本网站
            if not random_index_str:
                # 为当前的新用户在当前的session对象中生成索引
                self.random_index_str = self.__get_random_str()
                # 为当前新用户设置cookie
                self.handler.set_secure_cookie('__sson__', self.random_index_str)
                # 为当前用户生成保存其相关内容的字典对象
                ALL_USER_DIC[self.random_index_str] = {}

            # 当浏览器传来的cookie不为空的时候
            else:
                # 浏览器传来的cookie非法的时候
                if self.random_index_str not in ALL_USER_DIC.keys():
                    # 为当前非法用户生产索引
                    self.random_index_str = self.__get_random_str()
                    # 仅仅为当前非法用户生成其保存相关内容的字典对象, 避免合法老用户的字典对象被清空
                    ALL_USER_DIC[self.random_index_str] = {}

        # 不管当前session对象有没有对应的索引都应该为他设置起相关的信息保存(当然了, 到这一步的时候经过if条件语句的过滤, 剩下来的就是刚刚创建字典对象的新用户或者非法用户, 以及其他合法的老用户了)
        ALL_USER_DIC[self.random_index_str][key] = value

        # 将为以上的新用户或者非法用户设置cookie的操作放在这里本无可厚非. 但是将老用户的cookie也重新设置一遍, 其实是为老用户更新过期时间而做的
        self.handler.set_secure_cookie('__sson__', self.random_index_str)

    def __getitem__(self, key):
        # 获取当前用户cookie中保存的索引值, 注意加密方式返回的cookie的值是bytes类型的
        self.random_index_str = self.handler.get_secure_cookie('__sson__', None)
        # 若索引值为空表示当前用户是新用户, 则直接返回空, 程序到此终止
        if not self.random_index_str:
            return None

        # 索引不为空的时候
        else:
            self.random_index_str = str(self.random_index_str, encoding="utf-8")
            # 在服务器端为保存该索引值表示当前用户是非法用户,则直接返回空
            current_user = ALL_USER_DIC.get(self.random_index_str, None)
            if not current_user:
                return None
            else:
                # 直接返回合法用户指定的key的值, 没有则默认返回空
                return current_user.get(key, None)

