import requests

from dataclasses import dataclass
from datetime  import datetime
from dateutil.parser import isoparse
from typing import List, Dict, Any, Optional, Union
from config import settings

from logger import Logger

logger = Logger().get_logger()

@dataclass
class HostInfo:
    """
    HostInfo class to hold information about the host.
    """
    host_id: str
    hostname: str
    ip_address: str
    mac_address: str
    os: str
    os_version: str
    last_seen: str
    manufacturer: str
    model: str
    location: str
    agent_version: str
    status: str
    created: str
    updated: str
    cloud_provider: str
    first_seen: str

    def __post_init__(self):
        """
        Converts string date attributes to datetime objects without timezone information.
        """
        if isinstance(self.last_seen, str):
            self.last_seen = isoparse(self.last_seen).replace(tzinfo=None)
        if isinstance(self.created, str):
            self.created = isoparse(self.created).replace(tzinfo=None)
        if isinstance(self.updated, str):
            self.updated = isoparse(self.updated).replace(tzinfo=None)
        if isinstance(self.first_seen, str):
            self.first_seen = isoparse(self.first_seen).replace(tzinfo=None)

class DataNormalizer:
    """
    Class to normalize data from different sources.
    """
    def __init__(self):
        pass

    def get_nested(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], keys: List[Any],  default: Any = "") -> Any:
        """
        Safely retrieves a nested value from a dictionary or a list of dictionaries using a list of keys
        Similar to: data.get("a",{}).get("b",{})..........
        """
        for key in keys:
            try:
                if isinstance(data, dict):
                    data = data.get(key, default)
                elif isinstance(data, list) and isinstance(key, int):
                    data = data[key]
                else:
                    return default
            except (KeyError, IndexError, TypeError):
                return default
        return data

    def fetch_address_from_ip(self, ip_address: str) -> Optional[str]:
        """
        Fetching the address from the IP address.
        On sucessful response, city, region and country_name are extracted
        On error response, empty string is passed back
        """
        logger.info("Starting to fetch the address from the IP address")
        url = settings.IP_ADDRESS_API_URL.format(ip_address=ip_address)
        try:
            response = requests.Session().post(url)
            response.raise_for_status()  # Raises a HTTPError if the HTTP request returned an unsuccessful status code
            data = response.json()
            if data.get('error', False):
                error_reason = {
                    "url": response.url,
                    "status_code": response.status_code,
                    "error": data.get('reason', 'Unknown error')
                }
                logger.error(f'Error during fetching address from IP address due to reason: {error_reason}')
                return ""
            full_address = f'{data.get("city", "Unknown")}, {data.get("region", "Unknown")} {data.get("country_name", "Unknown")}'
            logger.info("Finished fetching the address from the IP address")
            return full_address
        except requests.RequestException as e:
            error_reason = {"url": response.url,"error":"Request failed: {e}"}
            logger.error(f'Error during fetching address from IP address due to reason: {error_reason}')
            return ""

    def normalize_qualys_data(self, data: List[Dict[str, Any]]) -> List[HostInfo]:
        """
        Normalizing Qualys data into HostInfo objects
        """
        normalized_data = []
        logger.info("Starting to normalize Qualys data into HostInfo objects")
        for item in data:
            normalized_item = HostInfo(
                host_id = str(item["_id"]),
                hostname = item.get("dnsHostName", ""),
                ip_address = item.get("address", ""),
                mac_address = self.get_nested(item, ["networkInterface", "list", 0, "HostAssetInterface", "macAddress"]),
                os_version = item.get("os", ""),
                os = self.get_nested(item, ["agentInfo", "platform"]),
                last_seen = item.get("modified", ""),
                manufacturer = item.get("manufacturer", ""),
                model = item.get("model", ""),
                location = self.get_nested(item, ["agentInfo", "location"]),
                agent_version = self.get_nested(item, ["agentInfo", "agentVersion"]),
                status = self.get_nested(item, ["agentInfo", "status"]),
                created = item.get("created", ""),
                updated = item.get("modified", ""),
                cloud_provider = item.get("cloudProvider"),
                first_seen = item.get("created", "")
            )
            normalized_data.append(normalized_item)
        logger.info("Completed normalizing Qualys data into HostInfo objects")
        return normalized_data

    def normalize_crowdstrike_data(self, data: List[Dict[str, Any]]) -> List[HostInfo]:
        """
        Normalizing CrowdStrike data into HostInfo objects
        """
        normalized_data = []
        logger.info("Starting to normalize CrowdStrike data into HostInfo objects")
        for item in data:
            normalized_item = HostInfo(
                host_id = item.get("device_id", ""),
                hostname = item.get("hostname", ""),
                ip_address = item.get("local_ip", ""),
                mac_address = item.get("mac_address"),
                os = item.get("platform_name", ""),
                os_version = item.get("os_version"),
                last_seen = item.get("last_seen", ""),
                manufacturer = item.get("system_manufacturer"),
                model = item.get("system_product_name"),
                location = self.fetch_address_from_ip(ip_address=item.get('external_ip')),
                agent_version = item.get("agent_version"),
                status = item.get("status", ""),
                created = item.get("first_seen", ""),
                updated = item.get("last_seen", ""),
                cloud_provider = item.get("service_provider"),
                first_seen = item.get("first_seen", "")
            )
            normalized_data.append(normalized_item)
        logger.info("Completed normalizing CrowdStrike data into HostInfo objects")
        return normalized_data

    def remove_duplicates(self, final_normalized_data: List[HostInfo]) -> List[HostInfo]:
        """
        Removing duplicate HostInfo objects
        """
        unique_hosts = {}
        logger.info("Starting to remove duplicate HostInfo objects")
        for host in final_normalized_data:
            if host.host_id in unique_hosts:
                if host.updated and (unique_hosts[host.host_id].updated is None \
                        or host.updated > unique_hosts[host.host_id].updated):
                    logger.info(
                        f"Duplicate found for host_id {host.host_id}. Replacing with newer data.\
                        Old updated: {unique_hosts[host.host_id].updated}, New updated: {host.updated}"
                    )
                    unique_hosts[host.host_id] = host
            else:
                unique_hosts[host.host_id] = host
        logger.info("Completed removing duplicate HostInfo objects")
        return list(unique_hosts.values())

data_normalizer = DataNormalizer()