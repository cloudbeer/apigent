class AlertDialog {
    constructor() {
        this.dialog = null;
        this.resolve = null;
        this.init();
    }

    init() {
        // 创建对话框 HTML
        const html = `
            <div id="alertDialog" class="fixed inset-0 bg-gray-600 bg-opacity-50 hidden overflow-y-auto h-full w-full z-50">
                <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                    <div class="mt-3">
                        <h3 class="text-lg font-medium text-gray-900 mb-4" id="alertTitle"></h3>
                        <p class="text-sm text-gray-500 mb-4" id="alertMessage"></p>
                        <div class="flex justify-end">
                            <button id="alertOk" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg">
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
        this.dialog = document.getElementById('alertDialog');
        this.title = document.getElementById('alertTitle');
        this.message = document.getElementById('alertMessage');
        this.okButton = document.getElementById('alertOk');

        // 绑定事件
        this.okButton.addEventListener('click', () => this.handleOk());
    }

    show(title, message) {
        this.title.textContent = title;
        this.message.textContent = message;
        this.dialog.classList.remove('hidden');

        return new Promise((resolve) => {
            this.resolve = resolve;
        });
    }

    handleOk() {
        this.dialog.classList.add('hidden');
        this.resolve();
    }
}

// 创建全局实例
window.alertDialog = new AlertDialog(); 