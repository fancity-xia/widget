import os
from pathlib import Path
import sys
from functools import lru_cache, wraps
import requests
import logging
from json.decoder import JSONDecodeError
from hashlib import sha256
sys.path.append(str(Path(__file__).absolute().parent))


LINK = os.environ.setdefault("PMS", "http://localhost:8080")  # PMS服务端口
DB = "/ais/dbOpers"  # 数据库操作接口
AUTH_TOKEN_API = "pms/auth"  # 权限申请接口
appKey = "Uk4**VRK"  # 权限申请appKey
appSecret = "eb4c58bece848********032f4b4eea37b0b7f0f896378041"


def parse_response(res):
    try:
        res_content = res.json()
    except JSONDecodeError as err:
        logging.error(f"无法解析返回值；返回值：{res}，错误信息：{err.msg}")
        return
    try:
        if res_content["code"] == 200:
            logging.info(f"命令执行成功！")
            logging.debug(f"{res_content['data']}")
            return res_content['data']
        elif res_content["code"] == 500:
            logging.info(f"命令执行失败；失败原因：{res_content['data']}")
            return
    except KeyError:
        logging.error(f"发生未知错误；返回值：{res_content}")
        return


def _pms_res_proc(func):
    """
    处理pms接口返回的结果
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        适用于类方法
        """
        res = func(*args, **kwargs)
        return parse_response(res)
    return wrapper


@_pms_res_proc
def _auth_code(app_key: str):
    """
    第一步，申请随机码code
        请求：GET https://xxx:8080/pms/auth/code?appKey=4Y2**8S
        响应：{"code":200,"message":"操作成功","data":"fdf2ec144c*******73a9cb49"}
        获取到的code使用一次后失效，且有效期5分钟
    """
    api_url = f"{LINK}/{AUTH_TOKEN_API}/code"
    logging.info(f"请求auth_code：")
    logging.debug(f"GET {api_url}?appKey={app_key}")
    res = requests.get(api_url, params={"appKey": app_key})
    return res


@lru_cache(maxsize=1)
def _auth_token(app_key: str, app_secret: str):
    """
    第二步，获取access_token
        请求：GET https://xxx:8080/pms/auth/accessToken?appKey=4Y2v**8S& \
        appSecret=f6148322a6e353a9****1cdc0a736a237b50125edec22cd068748ed4bd4&code=fdf2e****ee9073a9cb49
        其中appSecret传递的是密文，加密方法：appSecret=sha256(appSecret+code)
        响应：{"code":200,"message":"操作成功","data": \
        "eyJ0eXAiOiJKV1QiLCJhb****.eyJhdWQiOiI0WTJ2*****cCI6MTY4Mzg4MjUyM30.\
        NdtVtpt3yRmV39m*****J9iU4dIDBxK7XeeGM"}
    """
    auth_code = _auth_code(app_key)
    sha_as = sha256((app_secret + auth_code).encode()).hexdigest()
    api_url = f"{LINK}/{AUTH_TOKEN_API}/accessToken"
    logging.info(f"请求auth_token")
    logging.debug(f"GET {LINK}/{AUTH_TOKEN_API}/accessToken?appKey={app_key}&"
                  f"appSecret={sha_as}&code={auth_code}")
    res = requests.get(
        api_url,
        params={"appKey": app_key, "appSecret": sha_as, "code": auth_code}
    )
    return res


def pms_auth(func):
    """
    PMS鉴权方法
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        适用于类方法
        """
        old_cache_hits = _auth_token.cache_info().hits
        auth_token = _auth_token(appKey, appSecret)
        if _auth_token.cache_info().hits > old_cache_hits:
            logging.info(f"使用缓存auth_token")
        else:
            logging.info(f"auth_token请求成功")

        res = func(auth_token=auth_token, *args, **kwargs)
        return res
    return wrapper


@pms_auth
def test():
    """
    pms_auth 通过装饰器方法使用
    :return:
    """
    pass
