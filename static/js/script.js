// 初始化搜索功能
function initSearch() {
    const searchInput = document.getElementById('searchInput');
    const resultsContainer = document.getElementById('searchResults');
    let timeoutId = null;

    // 加载注释数据
    let comments = {};
    try {
        comments = JSON.parse(document.getElementById('comments-data').textContent);
        console.log('成功加载注释:', Object.keys(comments).length);
    } catch (e) {
        console.error('注释加载失败:', e);
    }

    // 获取配置项元素
    const configItems = Array.from(document.querySelectorAll('.config-item')).map(item => ({
        element: item,
        path: item.dataset.path || '',
        desc: item.querySelector('.config-description')?.textContent.trim() || '',
        title: item.querySelector('.config-title')?.textContent.trim() || ''
    }));

    // 搜索工具函数
    const escapeRegExp = (string) => string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const highlight = (text, keyword) => {
        if (!text || !keyword) return text;
        const regex = new RegExp(`(${escapeRegExp(keyword)})`, 'gi');
        return text.replace(regex, '<mark class="search-highlight">$1</mark>');
    };

    // 核心搜索逻辑
    const updateResults = (keyword) => {
        resultsContainer.innerHTML = '';
        if (!keyword) {
            resultsContainer.style.display = 'none';
            return;
        }

        const lowerKeyword = keyword.toLowerCase();
        const matches = configItems.filter(item => [
            item.path.toLowerCase(),
            item.title.toLowerCase(),
            item.desc.toLowerCase(),
            ...(comments[item.path] || []).join(' ').toLowerCase().split(' ')
        ].some(field => field.includes(lowerKeyword)));

        matches.forEach(item => {
            const div = document.createElement('div');
            div.className = 'search-item';
            div.innerHTML = `
                <div class="search-path">${highlight(item.path, keyword)}</div>
                <div class="search-meta">
                    ${item.desc ? `<div class="search-desc">${highlight(item.desc, keyword)}</div>` : ''}
                    ${comments[item.path]?.length ? 
                        `<div class="search-comment">💬 ${highlight(comments[item.path].join(' '), keyword)}</div>` : ''}
                </div>
            `;
            
            div.addEventListener('click', () => {
                item.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                item.element.classList.add('search-target-highlight');
                setTimeout(() => item.element.classList.remove('search-target-highlight'), 2000);
                resultsContainer.style.display = 'none';
            });
            
            resultsContainer.appendChild(div);
        });

        resultsContainer.style.display = matches.length ? 'block' : 'none';
    };

    // 事件监听
    searchInput.addEventListener('input', (e) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => updateResults(e.target.value.trim()), 300);
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-container')) {
            resultsContainer.style.display = 'none';
        }
    });

    // 键盘导航
    let selectedIndex = -1;
    document.addEventListener('keydown', (e) => {
        const items = resultsContainer.querySelectorAll('.search-item');
        if (!items.length) return;

        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                selectedIndex = (selectedIndex + 1) % items.length;
                break;
            case 'ArrowUp':
                e.preventDefault();
                selectedIndex = (selectedIndex - 1 + items.length) % items.length;
                break;
            case 'Enter':
                if (selectedIndex >= 0) items[selectedIndex].click();
                break;
        }

        items.forEach((item, index) => {
            item.classList.toggle('active', index === selectedIndex);
        });
    });
}

// 表单提交处理
async function handleSubmit(event) {
    event.preventDefault();
    console.log('[Submit] 开始保存配置');
    
    const form = event.target;
    const notification = showNotification('🔄 正在保存配置...', 'info');

    try {
        const formData = new FormData(form);
        // 打印表单数据，方便调试
        for (let [key, value] of formData.entries()) {
            console.log(`${key}: ${value}`);
        }

        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP错误 ${response.status}`);
        }

        const data = await response.json();
        showNotification('✅ 配置保存成功', 'success', 3000);
        console.log('[Submit] 保存成功:', data.config);
        // 刷新页面
        location.reload(); 
    } catch (error) {
        console.error('[Submit] 保存失败:', error);
        showNotification(`❌ 保存失败: ${error.message}`, 'error', 5000);
    }
}

// 显示通知
function showNotification(message, type = 'info', duration = 3000) {
    const container = document.getElementById('notification');
    const notification = document.createElement('div');
    
    notification.className = `notification notification-${type} animate-in`;
    notification.innerHTML = `
        <span class="notification-icon">${getIcon(type)}</span>
        <span class="notification-text">${message}</span>
    `;

    container.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('animate-out');
        setTimeout(() => notification.remove(), 500);
    }, duration);

    return notification;
}

// 获取通知图标
function getIcon(type) {
    const icons = {
        info: 'ℹ️',
        success: '✅',
        error: '❌',
        warning: '⚠️'
    };
    return icons[type] || '';
}

// 初始化应用
function initializeApp() {
    const form = document.getElementById('configForm');
    if (!form) {
        console.error('错误: 未找到配置表单');
        return;
    }

    form.addEventListener('submit', handleSubmit);
    initSearch();

    // 快捷键支持
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.getElementById('searchInput').value = '';
            document.getElementById('searchResults').style.display = 'none';
        }
    });
}

// 启动
document.addEventListener('DOMContentLoaded', initializeApp);