document.addEventListener('DOMContentLoaded', () => {
    const webrtcClient = new WebRTCClient();
    const startButton = document.getElementById('startButton');
    const stopButton = document.getElementById('stopButton');

    startButton.addEventListener('click', async () => {
        startButton.disabled = true;
        const initialized = await webrtcClient.init();
        
        if (initialized) {
            await webrtcClient.startConnection();
            stopButton.disabled = false;
        } else {
            startButton.disabled = false;
            alert('Failed to initialize WebRTC connection');
        }
    });

    stopButton.addEventListener('click', async () => {
        await webrtcClient.stopConnection();
        startButton.disabled = false;
        stopButton.disabled = true;
    });
}); 