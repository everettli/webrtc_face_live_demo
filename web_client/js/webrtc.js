class WebRTCClient {
    constructor() {
        this.peerConnection = null;
        this.dataChannel = null;
        this.localStream = null;
        this.websocket = null;
        
        this.configuration = {
            iceServers: [{
                urls: 'turn:127.0.0.1:3478',
                username: 'webrtc',
                credential: 'webrtc123'
            }]
        };
    }

    async init() {
        try {
            this.localStream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: false
            });
            document.getElementById('localVideo').srcObject = this.localStream;
            
            this.websocket = new WebSocket('ws://127.0.0.1:8088/ws');
            this.setupWebSocket();
            
            return true;
        } catch (error) {
            console.error('Error initializing WebRTC:', error);
            return false;
        }
    }

    setupWebSocket() {
        this.websocket.onmessage = async (event) => {
            const message = JSON.parse(event.data);
            
            if (message.type === 'answer') {
                await this.handleAnswer(message);
            } else if (message.type === 'candidate') {
                await this.handleCandidate(message);
            }
        };
    }

    async createPeerConnection() {
        this.peerConnection = new RTCPeerConnection(this.configuration);
        
        this.dataChannel = this.peerConnection.createDataChannel('detections');
        this.setupDataChannel();
        
        this.localStream.getTracks().forEach(track => {
            this.peerConnection.addTrack(track, this.localStream);
        });
        
        this.peerConnection.ontrack = (event) => {
            document.getElementById('remoteVideo').srcObject = event.streams[0];
        };
        
        this.peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                this.websocket.send(JSON.stringify({
                    type: 'candidate',
                    candidate: event.candidate
                }));
            }
        };
    }

    setupDataChannel() {
        this.dataChannel.onmessage = (event) => {
            const detections = JSON.parse(event.data);
            // Handle incoming detection data
            this.drawDetections(detections);
        };
    }

    drawDetections(detections) {
        // Implementation for drawing detection boxes on the video
        const video = document.getElementById('remoteVideo');
        const canvas = document.createElement('canvas');
        // Drawing logic here
    }

    async startConnection() {
        await this.createPeerConnection();
        const offer = await this.peerConnection.createOffer();
        await this.peerConnection.setLocalDescription(offer);
        
        this.websocket.send(JSON.stringify({
            type: 'offer',
            sdp: offer.sdp
        }));
    }

    async handleAnswer(answer) {
        await this.peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
    }

    async handleCandidate(message) {
        await this.peerConnection.addIceCandidate(new RTCIceCandidate(message.candidate));
    }

    async stopConnection() {
        if (this.peerConnection) {
            this.peerConnection.close();
            this.peerConnection = null;
        }
        
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
            this.localStream = null;
        }
        
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        document.getElementById('localVideo').srcObject = null;
        document.getElementById('remoteVideo').srcObject = null;
    }
} 