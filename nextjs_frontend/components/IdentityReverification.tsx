import React, { useState, useEffect } from 'react';

interface IdentityReverificationProps {
  username: string; // Add this prop type definition
}

const IdentityReverification: React.FC<IdentityReverificationProps> = ({ username }) => { 
  const [step, setStep] = useState(0);
  const [capturedImages, setCapturedImages] = useState<string[]>([]);
  const [videoStream, setVideoStream] = useState<MediaStream | null>(null);
  const expressions = ['快乐', '平静', '难过'];
  const [nextStep, setNextStep] = useState<'voice-confirmation' | 'face-verification' | null>(null);
  const [verificationData, setVerificationData] = useState<{ audio_url: string; transcription: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [noPendingFiles, setNoPendingFiles] = useState(false);

  const fetchVerificationData = async () => {
    setLoading(true);
    setNoPendingFiles(false);
    try {
      const response = await fetch('http://101.64.178.171:8001/fetch-verification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username }),
      });
      if (!response.ok) {
        throw new Error('Failed to fetch verification data');
      }
      const data = await response.json();
      if (data && data.audio_url && data.transcription) {
        setVerificationData(data);
      } else {
        setNoPendingFiles(true);
      }
    } catch (error) {
      console.error('Error fetching verification data:', error);
      setNoPendingFiles(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVerificationData();
  }, []);

  // Initialize and cleanup camera functions
  const initCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      setVideoStream(stream);
    } catch (error) {
      console.error('Error accessing the camera:', error);
      alert('无法访问摄像头，请检查权限设置。');
    }
  };

  const cleanupCamera = () => {
    if (videoStream) {
      videoStream.getTracks().forEach(track => track.stop());
      setVideoStream(null);
    }
  };

  // UseEffect to manage camera lifecycle for face verification
  useEffect(() => {
    if (nextStep === 'face-verification') {
      initCamera();
    } else {
      cleanupCamera();
    }
    return cleanupCamera; // Clean up on unmount
  }, [nextStep]);

  const handleCaptureImage = () => {
    const video = document.getElementById('camera') as HTMLVideoElement;
    if (!video) {
      alert('摄像头未初始化，请稍后再试。');
      return;
    }

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    if (context) {
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      const image = canvas.toDataURL('image/png');
      setCapturedImages(prevImages => [...prevImages, image]);
      if (step < 3) {
        setStep(step + 1);
      } else {
        setStep(0); // Reset step after capturing all images
        cleanupCamera(); // Stop the camera after capturing 3 images
      }
    }
  };
  const handleUpload = async () => {
    if (capturedImages.length !== 3) {
      alert('请确保已拍摄3张图片。');
      return;
    }
  
    try {
      const formData = new FormData();
      formData.append('username', username);
      if (verificationData && verificationData.audio_url) {
        formData.append('audio_url', verificationData.audio_url);
      }
      // Convert base64 image data to File objects and append to FormData
      capturedImages.forEach((imageData, index) => {
        // Extract base64 content from data URL
        const byteString = atob(imageData.split(',')[1]);
        const mimeString = imageData.split(',')[0].split(':')[1].split(';')[0];
  
        // Convert the byte string to an ArrayBuffer
        const arrayBuffer = new ArrayBuffer(byteString.length);
        const uint8Array = new Uint8Array(arrayBuffer);
        for (let i = 0; i < byteString.length; i++) {
          uint8Array[i] = byteString.charCodeAt(i);
        }
  
        // Create a Blob from the arrayBuffer
        const blob = new Blob([uint8Array], { type: mimeString });
  
        // Create a File instance for each image
        const file = new File([blob], `image${index + 1}.png`, { type: mimeString });
  
        // Append the File object to the FormData
        formData.append(`image${index + 1}`, file);
      });
  
      // Send the data to your server endpoint
      const response = await fetch('http://101.64.178.171:8001/upload-images', {
      method: 'POST',
      body: formData,
    });

    const result = await response.json();

    if (response.ok) {
      const userConfirmed = confirm(`${result.message}\n点击确定返回主页，或取消重新进行身份验证。`);
      if (userConfirmed) {
        setNextStep('voice-confirmation');// Redirect to the homepage
      } else {
        setNextStep('face-verification'); // Return to face verification step
      }
    } else {
      throw new Error(result.error || '上传失败');
    }
    } catch (error) {
      console.error('Upload error:', error);
      alert('上传失败，请重试。');
    }
  };
  
  const renderFaceVerification = () => (
    <>
      {step > 0 && step <= 3 && (
        <div>
          <video
            id="camera"
            autoPlay
            muted
            playsInline
            style={{ width: '100%', maxWidth: '400px', margin: '20px auto', display: 'block' }}
            ref={videoElement => {
              if (videoElement && videoStream) {
                videoElement.srcObject = videoStream;
              }
            }}
          ></video>
          <p>请展示 "{expressions[step - 1]}" 的表情并点击“拍摄”按钮。</p>
          <button onClick={handleCaptureImage}>拍摄</button>
        </div>
      )}
      {capturedImages.length > 0 && (
        <div>
          <h3>已拍摄的图片:</h3>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', border: '1px solid #ccc', padding: '10px' }}>
            {capturedImages.map((img, idx) => (
              <img
                key={idx}
                src={img}
                alt={`Captured ${expressions[idx]}`}
                style={{ width: '100px', height: 'auto', objectFit: 'cover', borderRadius: '8px' }}
              />
            ))}
          </div>
        </div>
      )}
      {capturedImages.length === 3 && (
        <div style={{ marginTop: '20px' }}>
          <p>已完成所有照片的拍摄。请继续进行下一步。</p>
          <button onClick={handleUpload}>上传图片</button>
        </div>
      )}
      {step === 0 && (
        <button onClick={() => setStep(1)}>开始身份验证</button>
      )}
    </>
  );

  const handleConfirmVoice = async (isUserVoice: boolean) => {
    try {
      if (!username) {
        alert('无法获取必要的音频数据或用户名。');
        return;
      }

      const response = await fetch('http://101.64.178.171:8001/confirm-verification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ isUserVoice, username }),
      });

      if (!response.ok) {
        throw new Error('确认失败');
      }

      const responseData = await response.json();
      alert(responseData.message);

      if (isUserVoice) {
        setNextStep('face-verification'); // Proceed to face verification
      } else {
        setStep(0); // Reset if not confirmed
      }
    } catch (error) {
      console.error('Confirmation error:', error);
      alert('确认失败，请重试。');
    }
  };

  return (
    <div>
      <h1>身份重新验证</h1>
      {nextStep === 'face-verification' ? (
        renderFaceVerification() // Render face verification steps
      ) : loading ? (
        <p>加载中...</p>
      ) : noPendingFiles ? (
        <div>
          <p>没有待查验的文件，您无法继续下一步。</p>
          <button onClick={fetchVerificationData}>刷新</button>
        </div>
      ) : verificationData ? (
        <div>
          <h2>待查验录音内容</h2>
          <p>{verificationData.audio_url}</p>
          <p>转录结果: {verificationData.transcription}</p>
          <button onClick={() => handleConfirmVoice(true)}>是我的请求</button>
          <button onClick={() => handleConfirmVoice(false)}>不是我的请求</button>
          <button onClick={fetchVerificationData} style={{ marginTop: '20px' }}>刷新</button>
        </div>
      ) : null}
    </div>
  );
};

export default IdentityReverification;
