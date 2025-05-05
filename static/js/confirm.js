class ConfirmDialog {
    constructor() {
        this.dialog = null;
        this.resolve = null;
        this.reject = null;
        this.init();
    }

    init() {
        // 创建对话框 HTML
        const html = `
            <div id="confirmDialog" class="fixed inset-0 bg-gray-600 bg-opacity-50 hidden overflow-y-auto h-full w-full z-50">
                <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                    <div class="mt-3">
                        <h3 class="text-lg font-medium text-gray-900 mb-4" id="confirmTitle"></h3>
                        <p class="text-sm text-gray-500 mb-4" id="confirmMessage"></p>
                        <div class="flex justify-end space-x-3">
                            <button id="confirmCancel" class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg">
                                取消
                            </button>
                            <button id="confirmOk" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg">
                                确定
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // 添加到 body
        const div = document.createElement('div');
        div.innerHTML = html;
        document.body.appendChild(div.firstElementChild);

        // 获取对话框元素
        this.dialog = document.getElementById('confirmDialog');
        this.title = document.getElementById('confirmTitle');
        this.message = document.getElementById('confirmMessage');
        this.okButton = document.getElementById('confirmOk');
        this.cancelButton = document.getElementById('confirmCancel');

        // 绑定事件
        this.okButton.addEventListener('click', () => this.handleOk());
        this.cancelButton.addEventListener('click', () => this.handleCancel());
    }

    show(title, message) {
        this.title.textContent = title;
        this.message.textContent = message;
        this.dialog.classList.remove('hidden');

        return new Promise((resolve, reject) => {
            this.resolve = resolve;
            this.reject = reject;
        });
    }

    handleOk() {
        this.dialog.classList.add('hidden');
        this.resolve(true);
    }

    handleCancel() {
        this.dialog.classList.add('hidden');
        this.resolve(false);
    }
}

// 创建全局实例
window.confirmDialog = new ConfirmDialog(); 