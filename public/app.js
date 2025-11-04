document.addEventListener('DOMContentLoaded', () => {
    const generateButton = document.getElementById('generate-button');
    const userInput = document.getElementById('user-input');
    const quoteDisplay = document.getElementById('quote-display');
    const loading = document.getElementById('loading');

    generateButton.addEventListener('click', async () => {
        const text = userInput.value.trim();
        if (!text) {
            quoteDisplay.textContent = '何か言葉を入力してください。';
            return;
        }

        // ローディング表示を見せ、前の結果をクリア
        loading.classList.remove('hidden');
        quoteDisplay.textContent = '';

        try {
            const response = await fetch('/api/generate_quote', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'APIからの応答エラー');
            }

            const data = await response.json();
            quoteDisplay.textContent = data.quote;

        } catch (error) {
            console.error('エラー:', error);
            quoteDisplay.textContent = `エラーが発生しました: ${error.message}`;
        } finally {
            // ローディング表示を隠す
            loading.classList.add('hidden');
        }
    });
});
