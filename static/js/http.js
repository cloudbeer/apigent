// API 请求的基础配置
const API_CONFIG = {
    baseURL: '',  // 可以根据需要设置基础 URL
    headers: {
        'Content-Type': 'application/json',
        'Custom-Language': localStorage.getItem('preferred_lang') || 'zh'
    }
};

// 通用请求方法
async function apiRequest(endpoint, options = {}) {
    const url = `${API_CONFIG.baseURL}${endpoint}`;
    const headers = {
        ...API_CONFIG.headers,
        ...options.headers
    };

    try {
        const response = await fetch(url, {
            ...options,
            headers
        });
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || '请求失败');
        }

        return data;
    } catch (error) {
        console.error('API 请求失败:', error);
        throw error;
    }
}

// GET 请求
async function apiGet(endpoint) {
    return apiRequest(endpoint);
}

// POST 请求
async function apiPost(endpoint, data) {
    return apiRequest(endpoint, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

// PUT 请求
async function apiPut(endpoint, data) {
    return apiRequest(endpoint, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

// DELETE 请求
async function apiDelete(endpoint) {
    return apiRequest(endpoint, {
        method: 'DELETE'
    });
}

// 导出方法
window.api = {
    get: apiGet,
    post: apiPost,
    put: apiPut,
    delete: apiDelete
}; 