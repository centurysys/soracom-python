# -*- coding: utf-8 -*-

"""SORACOM API client module"""

import os
import datetime
import client


class SpeedClass(object):
    class s1(object):
        minimum  = "s1.minimum"
        slow     = "s1.slow"
        standard = "s1.standard"
        fast     = "s1.fast"


class Status(object):
    active     = "active"
    inactive   = "inactive"
    ready      = "ready"
    instock    = "instock"
    shipped    = "shipped"
    suspended  = "suspended"
    terminated = "terminated"


class Period(object):
    minutes = "minutes"
    day     = "day"
    month   = "month"


class SoracomAPI(object):
    """Soracom API Client Class"""

    def __init__(self, email=os.environ.get("SORACOM_EMAIL"),
                 password=os.environ.get("SORACOM_PASSWORD")):
        self._client = client.SoracomClient()
        self._authInfo = self._client.auth(email, password)

    # 特定Operator下のSubscriber一覧を取得
    def list_subscribers(self, limit=1024, filter={}):
        uri = "/subscribers"
        params = {"limit" : limit}

        if "imsi" in filter:
            uri = "/subscribers/%s" % filter["imsi"]
        elif "status" in filter:
            params["status_filter"] = filter["status"]
        elif "speed_class" in filter:
            params["speed_class_filter"] = filter["speed_class"]

        return self._client.get(uri, params)

    def subscribers(self, limit=1024, filter={}):
        return self.list_subscribers(limit, filter)

    # SIMの登録
    def register_subscriber(self, imsi, registration_secret="", groupId=None, tags={})
        if not imsi:
            return {}

        uri = "/subscribers/%s/register" % imsi
        params = {"registrationSecret" : registration_secret,
                  "tags"               : tags}
        if groupId:
            params["groupId"] = groupId

        return self._client.post(uri, params)

    def __operate_subscriber(self, method, operation, imsis, params={}):
        if type(imsis) != list:
            imsis = [imsis]

        results = {}
        for imsi in imsis:
            uri = "/subscribers/%s/%s" % (imsi, operation)

            if method == "POST":
                res = self._client.post(uri, params)
            elif method == "PUT":
                res = self._client.put(uri, params)
            elif method == "DELETE":
                res = self._client.delete(uri)

            results[imsi] = res

        return res

    # SIMの利用開始(再開)
    def activate_subscriber(self, imsis):
        return self.__operate_subscriber("POST", "activate", imsis)

    # SIMの利用休止
    def deactivate_subscriber(self, imsis):
        return self.__operate_subscriber("POST", "deactivate", imsis)

    # SIMの解約
    def terminate_subscriber(self, imsis):
        return self.__operate_subscriber("POST", "terminate", imsis)

    # 指定されたSubscriberをTerminate可能に設定する
    def enable_termination(self, imsis):
        return self.__operate_subscriber("POST", "enable_terminate", imsis)

    # 指定されたSubscriberをTerminate不可能に設定する
    def disable_termination(self, imsis):
        return self.__operate_subscriber("POST", "disable_terminate", imsis)

    # タグの更新
    def update_subscriber_tags(self, imsis, tags):
        return self.__operate_subscriber("PUT", "tags", imsis, tags)

    # 指定タグの削除
    def delete_subscriber_tag(self, imsis, tag_name):
        return self.__operate_subscriber("DELETE", "tags/%s" % tag_name, imsis)

    # SIMのプラン変更
    def update_subscriber_speed_class(self, imsis, speed_class):
        params = {"speedClass" : speed_class}
        return self.__operate_subscriber("POST", "update_speed_class", imsis,
                                         params)

    # SIMの有効期限設定
    def set_expiry_time(self, imsis, expiry_time):
        params = {"expiryTime" : expiry_time}
        return self.__operate_subscriber("POST", "set_expiry_time", imsis,
                                         params)

    # SIMの有効期限設定を解除
    def unset_expiry_time(self, imsis):
        return self.__operate_subscriber("POST", "unset_expiry_time", imsis)

    # SIMの所属Groupを指定あるいは上書き変更
    def set_group(self, imsi, group_id):
        params = {"groupdId" : group_id}
        return self.__operate_subscriber("POST", "set_group", imsis, params)

    # SIMの所属Groupを指定を解除
    def unset_group(self, imsi):
        return self.__operate_subscriber("POST", "unset_group", imsis)

    # SIMグループの一覧を取得
    def list_groups(self, group_id=""):
        if not group_id:
            uri = "/groups"
        else:
            uri = "/groups/%s" % group_id

        return self._client.get(uri)

    def __get_usage(self, kind, imsi, time_from, time_to, period):
        if not imsi:
            return []

        now = datetime.datetime.now()

        if not time_from:
            tmp = now - datetime.timedelta(days=1)
            time_from = int(tmp.timestamp())

        if not time_to:
            time_to = int(now.timestamp())

        uri = "/stats/%s/subscribers/%s" % (kind, imsi)
        params = {"from"   : time_from,
                  "to"     : time_to,
                  "period" : period}

        return self._client.get(uri, params)

    # Subscriber毎のAir使用状況を得る(デフォルトでは直近１日)
    def get_air_usage(self, imsi=None, time_from=None, time_to=None, period="minutes"):
        return self.__get_usage("air", imsi, time_from, time_to, period)

    # Subscriber毎のBeam使用状況を得る(デフォルトでは直近１日)
    def get_beam_usage(self, imsi=None, time_from=None, time_to=None, period="minutes"):
        return self.__get_usage("beam", imsi, time_from, time_to, period)

    # APIキーを取得
    def get_api_key(self):
        return self._authInfo["apiKey"]

    # オペレータIDを取得
    def get_operator_id(self):
        return self._authInfo["operatorId"]

    # トークンを取得
    def get_token(self):
        return self._authInfo["token"]
