import { API_SITES } from './thirdparty'

export async function searchThirdPartySource(movieName, sourceKey = 'dyttzy') {
    const site = API_SITES[sourceKey];
    const thirdPartyUrl = `${site.api}?ac=detail&wd=${encodeURIComponent(movieName)}`;
    const encodedUrl = encodeURIComponent(thirdPartyUrl);
    try {
        // 请求自己的后端代理API（修正路径）
        const res = await fetch(`/api/thirdparty-proxy/?url=${encodedUrl}`);
        const data = await res.json();
        if (data && data.list && data.list.length > 0) {
            const playUrl = data.list[0].vod_play_url;
            const m3u8 = playUrl.split('$').pop();
            return m3u8;
        }
        return null;
    } catch (e) {
        return null;
    }
} 