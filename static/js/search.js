class ConfigSearch {
    constructor() {
        this.searchInput = document.getElementById('searchInput');
        this.resultsContainer = document.getElementById('searchResults');
        this.comments = this.loadComments();
        this.configItems = [];
        this.init();
    }

    init() {
        console.log('[Search] 初始化配置搜索');
        this.buildIndex();
        this.setupEventListeners();
        window.debugSearch = this; // 暴露调试接口
    }

    loadComments() {
        try {
            const dataElement = document.getElementById('comments-data');
            if (!dataElement) throw new Error('找不到注释数据容器');
            
            const comments = JSON.parse(dataElement.textContent);
            console.log('[Search] 加载注释项:', Object.keys(comments).length);
            return comments;
        } catch (error) {
            console.error('[Search] 注释加载失败:', error);
            return {};
        }
    }

    buildIndex() {
        this.configItems = Array.from(document.querySelectorAll('.config-item')).map(item => {
            const path = item.dataset.path;
            if (!path) console.warn('配置项缺失data-path:', item);
            
            return {
                element: item,
                path: path || '',
                title: item.querySelector('.config-title')?.textContent?.trim() || '',
                desc: item.querySelector('.config-description')?.textContent?.trim() || '',
                value: item.querySelector('input,select,textarea')?.value || ''
            };
        });
        console.log('[Search] 建立索引项:', this.configItems.length);
    }

    search(keyword) {
        const cleanKeyword = keyword.trim().toLowerCase();
        if (!cleanKeyword) return [];

        return this.configItems.filter(item => {
            // 多字段匹配
            const fields = [
                item.path,
                item.title,
                item.desc,
                item.value,
                ...(this.comments[item.path] || [])
            ].join('|').toLowerCase();

            return fields.includes(cleanKeyword);
        });
    }

    highlight(text, keyword) {
        if (!text || !keyword) return text;
        const regex = new RegExp(`(${this.escapeRegExp(keyword)})`, 'gi');
        return text.replace(regex, '<mark class="search-highlight">$1</mark>');
    }

    escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    renderResults(keyword) {
        this.resultsContainer.innerHTML = '';
        if (!keyword) return;

        const results = this.search(keyword);
        if (results.length === 0) {
            this.resultsContainer.innerHTML = '<div class="search-empty">🔍 未找到匹配项</div>';
            return;
        }

        this.resultsContainer.innerHTML = results.map(item => `
            <div class="search-item" data-path="${item.path}">
                <div class="search-path">${this.highlight(item.path, keyword)}</div>
                ${item.title ? `<div class="search-title">${this.highlight(item.title, keyword)}</div>` : ''}
                ${item.desc ? `<div class="search-desc">${this.highlight(item.desc, keyword)}</div>` : ''}
                ${this.comments[item.path]?.length ? 
                    `<div class="search-comment">📌 ${this.highlight(this.comments[item.path].join(' '), keyword)}</div>` : ''}
            </div>
        `).join('');

        // 绑定点击事件
        this.resultsContainer.querySelectorAll('.search-item').forEach(el => {
            el.addEventListener('click', () => {
                const targetItem = this.configItems.find(i => i.path === el.dataset.path);
                if (targetItem) {
                    targetItem.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    targetItem.element.classList.add('search-target-highlight');
                    setTimeout(() => {
                        targetItem.element.classList.remove('search-target-highlight');
                    }, 2000);
                }
            });
        });
    }

    setupEventListeners() {
        // 输入防抖 (300ms)
        let timeout;
        this.searchInput.addEventListener('input', (e) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                this.renderResults(e.target.value.trim());
            }, 300);
        });

        // 全局点击关闭
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                this.resultsContainer.innerHTML = '';
            }
        });

        // 快捷键
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.searchInput.value = '';
                this.resultsContainer.innerHTML = '';
            }
        });
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    new ConfigSearch();
});