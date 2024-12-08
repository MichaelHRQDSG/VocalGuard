'use client';  // Ensure the code is rendered on the client-side

import React, { useState, useEffect } from 'react';
import './globals.css';  // Import global styles

import ImageSlider from './components/ImageSlider'; // Import the ImageSlider component
import CompanyDocumentUpload from './components/CompanyDocumentUpload';
import IdentityReverification from './components/IdentityReverification';
import {LineChart } from "./components/Charts";



interface DetectionData {
  transcription: string;
  task: string;
  deepfake: {
    completed: boolean;
    result: {
      confidence: number;
    };
  };
  query_speakers: {
    completed: boolean;
    result: Record<string, any>; // Adjust the type based on your actual data structure
  };
  detection_context: {
    completed: boolean;
    result: Record<string, any>; // Adjust as needed
  };
  // Add other properties if needed
}

// Main component for the Home page
export default function Home() {
  // State variables to manage different data and UI components
  const [audioFile, setAudioFile] = useState<File | null>(null); // State to store the uploaded audio file
  const [result, setResult] = useState(''); // State to store the result from the backend
  const [selectedTab, setSelectedTab] = useState('intro'); // State for the currently selected navigation tab
  const [threatData, setThreatData] = useState<any[]>([]); // State to store threat monitoring data from the backend
  const [email, setEmail] = useState(''); // State to store the user's email input
  const [password, setPassword] = useState(''); // State to store the user's password input
  const [isLoginMode, setIsLoginMode] = useState(true); // State to toggle between login and register modes
  const [authResult, setAuthResult] = useState(''); // State to store authentication result messages
  const [isLoggedIn, setIsLoggedIn] = useState(false); // State to track if the user is logged in
  const [showLoginPrompt, setShowLoginPrompt] = useState(false); // State to control the visibility of the login prompt
  const [isLoading, setIsLoading] = useState(false); // State to track loading status
  const [selectedUploadType, setSelectedUploadType] = useState('urlText'); // State to track the selected upload type
  const [urlText, setUrlText] = useState(''); // State to store the user's URL or text input
  const [emailText, setEmailText] = useState(''); // State to store email text input
  const [level, setLevel] = useState('Standard'); // State to store user level
  const [personalIntro, setPersonalIntro] = useState(''); // State for personal introduction
  const [profilePhoto, setProfilePhoto] = useState<File | null>(null); // State for profile photo
  const [audioInfo, setAudioInfo] = useState<File | null>(null); // State for audio information
  const [detectionData, setDetectionData] = useState<DetectionData | null>(null);
  const [selectedThreatFile, setSelectedThreatFile] = useState(''); // State to store selected threat filename
  const [solutionContent, setSolutionContent] = useState(''); // State to store solution content

  
  const lineData = [
    { label: "Jan", value: 100 },
    { label: "Feb", value: 200 },
    { label: "Mar", value: 150 },
    { label: "Apr", value: 300 },
  ];
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setAudioFile(e.target.files[0]);
    }
    // Reset the input value to allow selecting the same file again
    e.target.value = '';
  };

  const handleUrlTextUpload = async () => {
    const response = await fetch('http://101.64.178.171:8001/upload-url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: urlText }), // Send urlText in the body
    });

    if (response.ok) {
      const data = await response.json();
      setResult(data.result); // Assuming the backend sends the result
    } else {
      alert('上传失败');
    }
  };

  // Email upload logic
  const handleEmailUpload = async () => {
    const response = await fetch('http://101.64.178.171:8001/upload-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ emailText }), // Send emailText in the body
    });

    if (response.ok) {
      const data = await response.json();
      setResult(data.result); // Assuming the backend sends the result
    } else {
      alert('上传失败');
    }
  };

  const handleUrlTextDetection = async () => {
    // 处理网址或文本的检测逻辑
    alert(`开始检测网址或文本: ${urlText}`);
    // 这里可以添加向后端发送请求的代码
  };
  
  const handleEmailDetection = async () => {
    // 处理邮件文本的检测逻辑
    alert(`开始检测邮件文本: ${emailText}`);
    // 这里可以添加向后端发送请求的代码
  };
  // Function to remove the selected audio file
  const handleRemoveFile = () => {
    setAudioFile(null);
  };
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!audioFile) {
        alert("请先选择一个音频文件。");
        return;
    }

    try {
        // Create a new FormData instance
        const formData = new FormData();
        
        // Append the audio file to the FormData object
        formData.append('audioFile', audioFile); // 'audioFile' is the key

        // Example user information
        const userInfo = {
            name: email, // Use the user's email as the name
            level: level, // Use the selected level
            detection_info: false // Example detection information
        };

        // Append the user information as a JSON string
        formData.append('userInfo', JSON.stringify(userInfo));

        // Send the POST request with FormData
        const response = await fetch('http://101.64.178.171:8001/upload_dataform', {
            method: 'POST',
            body: formData // Use FormData as the body
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(`上传失败：${errorData.error || "未知错误"}`);
            return;
        }

        const data = await response.json();
        alert(`上传成功！音频 ID: ${data.audio_id}`);
        setResult(data.audio_id);

    } catch (error) {
        console.error("Upload error:", error);
        alert("上传过程中发生错误，请重试。");
    }
};
 
const handleProfilePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  if (e.target.files) {
    setProfilePhoto(e.target.files[0]);
  }
};

// Handler for audio information change
const handleAudioChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  if (e.target.files) {
    setAudioInfo(e.target.files[0]);
  }
};

// Function to handle personal information upload
// const handlePersonalInfoUpload = async (e: React.FormEvent) => {
//   e.preventDefault();

//   if (!profilePhoto || !audioInfo || !personalIntro) {
//     alert("请确保上传所有信息。");
//     return;
//   }

//   // Convert the profile photo and audio info to base64 strings
//   const profilePhotoBase64 = await convertToBase64(profilePhoto);
//   const audioInfoBase64 = await convertToBase64(audioInfo);

//   // Construct the JSON data
//   const data = {
//     userInfo: {
//       name: email, // Replace with actual user name
//       level: level, // Replace with actual user level
//     },
//     profilePhoto: profilePhotoBase64,
//     audioInfo: audioInfoBase64,
//     personalIntro: personalIntro,
//   };

//   try {
//     const response = await fetch('http://101.64.178.171:8001/upload-personal-info', {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//       },
//       body: JSON.stringify(data),
//     });

//     if (response.ok) {
//       const responseData = await response.json();
//       alert(`上传成功！消息: ${responseData.message}`);
//     } else {
//       alert("上传失败，请稍后重试。");
//     }
//   } catch (error) {
//     console.error("Error uploading personal information:", error);
//     alert("上传过程中发生错误，请重试。");
//   }
// };
const handlePersonalInfoUpload = async (e: React.FormEvent) => {
  e.preventDefault();

  if (!profilePhoto || !audioInfo || !personalIntro) {
    alert("请确保上传所有信息。");
    return;
  }

  // Create a FormData object
  const formData = new FormData();
  formData.append('userInfo', JSON.stringify({
    name: email, // Replace with actual user name
    level: level, // Replace with actual user level
  }));
  formData.append('profilePhoto', profilePhoto); // Assuming `profilePhoto` is a file object
  formData.append('audioInfo', audioInfo); // Assuming `audioInfo` is a file object
  formData.append('personalIntro', personalIntro);

  try {
    const response = await fetch('http://101.64.178.171:8001/upload-personal-info', {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const responseData = await response.json();
      alert(`上传成功！消息: ${responseData.message}`);
    } else {
      alert("上传失败，请稍后重试。");
    }
  } catch (error) {
    console.error("Error uploading personal information:", error);
    alert("上传过程中发生错误，请重试。");
  }
};
// Helper function to convert file to base64
const convertToBase64 = (file: File): Promise<string | ArrayBuffer | null> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
  });
};

  // useEffect to fetch threat monitoring data from the backend when the tab is selected
  const fetchThreatData = async () => {
    try {
      const response = await fetch('http://101.64.178.171:8001/threat-monitoring');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setThreatData(data);
    } catch (error) {
      console.error('Error fetching threat data:', error);
    }
  };
  const fetchSolutionContent = async (filename: string) => {
    try {
      // Remove the ".json" extension from the filename
    console.log('Original filename:', filename); // Debugging log
    const cleanFilename = filename.trim(); // Trim any white spaces
    const baseFilename = cleanFilename.endsWith('.json') ? cleanFilename.slice(0, -5) : cleanFilename;
    console.log('Base filename after removing .json:', baseFilename); // Verify base filename
      const response = await fetch(`http://101.64.178.171:8001/get_solution/${baseFilename}_solution.json`);
      const url = `http://101.64.178.171:8001/get_solution/${baseFilename}_solution.json`;
      console.log('Fetching URL:', url); // Log the URL to ensure it's correct

      if (!response.ok) {
        throw new Error('Failed to fetch solution content');
      }
      const data = await response.json();
      setSolutionContent(JSON.stringify(data, null, 2)); // Format content for display
    } catch (error) {
      console.error('Error fetching solution content:', error);
      setSolutionContent('Failed to load solution content.');
    }
  };

  // useEffect to fetch threat monitoring data from the backend when the tab is selected
  useEffect(() => {
    if (selectedTab === 'threat-monitoring') {
      fetchThreatData(); // Fetch data when the tab is selected
    }
  }, [selectedTab]);

  // Function to handle refreshing the threat data
  const handleRefreshThreatData = () => {
    fetchThreatData(); // Call the fetch function to get the latest data
  };

  // Function to handle login or register form submission
  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
  
    const endpoint = isLoginMode ? 'login' : 'register';
    const controller = new AbortController(); // Create an AbortController instance
    const timeoutId = setTimeout(() => {
      controller.abort(); // Abort the request after 2 seconds
    }, 2000);
  
    try {
      const response = await fetch(`http://101.64.178.171:8001/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, level }),
        signal: controller.signal, // Pass the signal to the fetch request
      });
  
      clearTimeout(timeoutId); // Clear the timeout if the request completes in time
  
      const data = await response.json();
      setAuthResult(data.message); // Store the response message
  
      if (response.ok && isLoginMode) {
            setIsLoggedIn(true);
            setLevel(data.level); // 确保更新 level
            setSelectedTab('intro');
            setAuthResult('');
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        // Handle the timeout case
        alert("请求超时，请重试。");
      } else {
        console.error("Error during authentication:", error); // Log other errors
        alert("发生错误，请重试。");
      }
    }
  };
  // Function to handle tab selection and navigation
  const handleTabClick = (tab: string) => {
    const restrictedTabs = ['threat-monitoring', 'company-document-upload', 'solutions'];
    if (restrictedTabs.includes(tab) && level !== 'Guard') {
      alert('您无权访问此页面。');
      return;
    }
    const allowedTabs = [
      'intro',
      'login',
      'upload',
      'threat-monitoring',
      'personal-information-upload',
      'company-document-upload',
      're-verification',
      'solutions',
    ];
    if (allowedTabs.includes(tab)) {
      if (tab === 'intro' || tab === 'login' || isLoggedIn) {
        setSelectedTab(tab);
      } else {
        setShowLoginPrompt(true);
      }
    }
  };

  
  // Function to handle audio detection
  const handleDetection = async () => {
    if (!audioFile) {
      alert("请先上传音频文件。"); // Alert if no file is selected
      return;
    }
  
    try {
      // Request to start detection on the backend
      const response = await fetch('http://101.64.178.171:8001/start-detection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ audioId: result }),
      });
  
      let data;
      try {
        data = await response.json(); // Attempt to parse the response as JSON
      } catch (parseError) {
        console.error("Response parsing error:", parseError);
        alert("收到的响应格式无效，请联系支持团队。");
        return;
      }
  
      if (response.ok) {
        alert("检测成功，请查看结果。"); // Alert if detection starts successfully
        console.log(data); // Log detection data
        setDetectionData(data); // Store the detection data
      } else {
        console.error("Detection failed with response:", data);
        alert("检测失败，请稍后重试。"); // Alert if detection fails
      }
    } catch (error) {
      console.error("Detection error:", error); // Log error to the console
      alert("检测过程中发生错误。"); // Alert if an error occurs
    }
  };

  const handlesmallDetection = async () => {
    if (!audioFile) {
      alert("请先上传音频文件。"); // Alert if no file is selected
      return;
    }
  
    try {
      // Request to start detection on the backend
      const response = await fetch('http://101.64.178.171:8001/start-smalldetection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ audioId: result }),
      });
  
      let data;
      try {
        data = await response.json(); // Attempt to parse the response as JSON
      } catch (parseError) {
        console.error("Response parsing error:", parseError);
        alert("收到的响应格式无效，请联系支持团队。");
        return;
      }
  
      if (response.ok) {
        alert("检测成功，请查看结果。"); // Alert if detection starts successfully
        console.log(data); // Log detection data
        setDetectionData(data); // Store the detection data
      } else {
        console.error("Detection failed with response:", data);
        alert("检测失败，请稍后重试。"); // Alert if detection fails
      }
    } catch (error) {
      console.error("Detection error:", error); // Log error to the console
      alert("检测过程中发生错误。"); // Alert if an error occurs
    }
  };
  const renderThreatDataList = () => {
    if (threatData.length === 0) {
      return <p>No threats found or loading...</p>;
    }

    // 按照 threat_score 从高到低排序
    const sortedThreatData = [...threatData].sort((a, b) => (b.threat_score || 0) - (a.threat_score || 0));

    return (
      <ul className="threat-list">
        {sortedThreatData.map((item, index) => {
          // Calculate a gradient color based on the threat score
          const threatScore = Math.min(Math.max(item.threat_score || 0, 0), 100);
          // Calculate red intensity based on threat score
          const red = Math.floor(255 * (threatScore / 100)); // Ranges from light to full red
          const green = Math.floor(255 * (1 - threatScore / 100)); // Ranges from full green to none
          const blue = Math.floor(255 * (1 - threatScore / 100)); // Ranges from full blue to none
          const alpha = 0.8; // Set transparency level

          const gradientColor = `rgba(${red}, ${green}, ${blue}, ${alpha})`;

          return (
            <li
              key={index}
              className="threat-item"
              style={{
                background: `linear-gradient(90deg, ${gradientColor}, white)`,
                transition: 'all 0.3s ease-in-out',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.transform = 'scale(1.02)')}
              onMouseLeave={(e) => (e.currentTarget.style.transform = 'scale(1)')}
            >
              <span className="data-description">
                用户名: {item.user_name}, 身份: {item.user_level}, 威胁分数: {item.threat_score}, 文件名: {item.filename}
              </span>
              <button
                className="query-btn"
                onClick={() => {
                  setSelectedThreatFile(item.filename); // Assuming item contains a filename property
                  fetchSolutionContent(item.filename);
                  setSelectedTab('solutions'); // Navigate to solutions tab
                }}
              >
                查询
              </button>
            </li>
          );
        })}
      </ul>
    );
  };

  const renderDetectionData = () => {
    if (!detectionData) return null; // 如果没有数据，则不渲染任何内容

    // 判断是否是合成音频
    const isSyntheticAudio =
        detectionData.deepfake.result?.confidence !== undefined &&
        detectionData.deepfake.result.confidence > 0.5;

    return (
        <div className="detection-results-container">
            <h3 className="title">检测结果</h3>

            {/* Deepfake 分析 */}
            <div className="analysis-card deepfake-analysis">
                <h4 className="card-title">Deepfake 分析</h4>
                <p><strong>是否完成:</strong> {detectionData.deepfake.completed ? '是' : '否'}</p>
                <p><strong>可信度:</strong> {detectionData.deepfake.result?.confidence !== undefined ? detectionData.deepfake.result.confidence : '无数据'}</p>
                <p><strong>是否是合成音频:</strong> {isSyntheticAudio ? '是真实音频' : '是合成音频'}</p>
            </div>

            {/* 查询说话人分析 */}
            <div className="analysis-card query-speakers-analysis">
                <h4 className="card-title">查询说话人分析</h4>
                <p><strong>是否完成:</strong> {detectionData.query_speakers.completed ? '是' : '否'}</p>
                <p><strong>分析结果:</strong> {JSON.stringify(detectionData?.speaker_id ||'无')}</p>
                <p><strong>相似度:</strong> {JSON.stringify(detectionData.query_speakers.result)}</p>
            </div>

            {/* 检测上下文分析 */}
            <div className="analysis-card detection-context-analysis">
                <h4 className="card-title">检测上下文分析</h4>
                <p><strong>是否完成:</strong> {detectionData.detection_context.completed ? '是' : '否'}</p>
                <p><strong>转录结果:</strong> {detectionData?.transcription || '无'}</p>
                <p><strong>分类分析结果:</strong> {JSON.stringify(detectionData.detection_context.result)}</p>
            </div>
        </div>
    );
};

  const renderFormattedSolutionContent = () => {
    if (!solutionContent) {
      return <p>No solution content available.</p>;
    }
  
    try {
      const parsedData = JSON.parse(solutionContent);
      const { original_json: originalJson, department_solutions: departmentSolutions } = parsedData;
      const llamaResponse = parsedData.llama3_response || '';
  
      // Split and trim lines for improved display
      const lines = llamaResponse
        .split(/[\r\n]+/)
        .map((line:string) => line.trim())
        .filter((line:string) => line);
  
      return (
        <div className="solution-content-container">
          <h2 className="solution-title">Detection Results and Response Plan</h2>
  
          {/* Display original_json details */}
          <div className="detection-summary">
            <h3>Detection Summary</h3>
            {originalJson && (
              <>
                <p><strong>User Name:</strong> {originalJson.user_name || 'N/A'}</p>
                <p><strong>User Level:</strong> {originalJson.user_level || 'N/A'}</p>
                <p><strong>Is Synthetic:</strong> {originalJson.is_synthetic ? 'Yes' : 'No'}</p>
                <p><strong>Is Specified Speaker:</strong> {originalJson.is_specified_speaker ? 'Yes' : 'No'}</p>
                <p><strong>Speaker ID:</strong> {originalJson.speaker_id || 'N/A'}</p>
                <p><strong>Transcription:</strong> {originalJson.transcription || 'N/A'}</p>
                <p><strong>Task:</strong> {originalJson.task || 'N/A'}</p>
                <p><strong>Deepfake Detection Completed:</strong> {originalJson.deepfake?.completed ? 'Yes' : 'No'}</p>
                <p><strong>Deepfake Confidence:</strong> {originalJson.deepfake?.result?.confidence || 'N/A'}</p>
                <p><strong>Query Speakers Completed:</strong> {originalJson.query_speakers?.completed ? 'Yes' : 'No'}</p>
                <p><strong>Query Speakers Similarity:</strong> {originalJson.query_speakers?.result?.similarity || 'N/A'}</p>
                <p><strong>Detection Context Classification Result:</strong> {originalJson.detection_context?.result?.classification_result || 'N/A'}</p>
                <p style={{ textAlign: 'center' }}><strong>Threat Score:</strong> {originalJson.threat_score || 'N/A'}</p>
              </>
            )}
          </div>
  
          {/* Display department_solutions */}
          {departmentSolutions && (
            <div className="department-solutions">
              <h3>Department Solutions</h3>
              {Object.entries(departmentSolutions).map(([department, solution], index) => (
                <div key={index} className="department-solution">
                  <h4>{department.replace(/_/g, ' ')}</h4>
                  <p>{solution as string}</p> {/* Type assertion */}
                </div>
              ))}
            </div>
          )}
  
          {/* Render the llamaResponse content */}
          <div className="response-plan-section">
            <div className="response-plan-content">
              {lines.map((line:string, index:number) => {
                const isDashLine = line.startsWith('-');
                const isTaskLine = isDashLine && line.toLowerCase().includes('task');
  
                return (
                  <p
                    key={index}
                    style={{
                      textAlign: isTaskLine ? 'center' : 'left',
                      margin: '10px 0',
                      fontSize: isTaskLine ? '1.5em' : '1em',
                      fontWeight: isTaskLine ? 'bold' : 'normal',
                    }}
                  >
                    {line}
                  </p>
                );
              })}
            </div>
          </div>
        </div>
      );
    } catch (error) {
      console.error('Error parsing solution content:', error);
      return <p>Invalid solution content format.</p>;
    }
  };
  
  
  

  // Function to render different content based on the selected tab
  const renderContent = () => {
    switch (selectedTab) {
      case 'intro':
        return <div className="image-slider-wrapper">
        <ImageSlider />
      </div>;

      case 'upload':
        return (
          <div className="content">
            <div className="header-container">
            <h1>欢迎来到页面</h1>
            </div>
            <h2>输入网站 URL 或文本</h2>
            <p>请在下方输入网址或长文本进行分析。</p>
            <div className="tabs">
              <button className={`tab ${selectedUploadType === 'urlText' ? 'active' : ''}`} onClick={() => setSelectedUploadType('urlText')}>网站 URL/文本</button>
              <button className={`tab ${selectedUploadType === 'audio' ? 'active' : ''}`} onClick={() => setSelectedUploadType('audio')}>通话音频</button>
              <button className={`tab ${selectedUploadType === 'emailText' ? 'active' : ''}`} onClick={() => setSelectedUploadType('emailText')}>邮件文本</button>
            </div>

            {/* Conditionally render content based on selected upload type */}
            {selectedUploadType === 'urlText' && (
              <div className="upload-section">
                <h2>输入网站 URL 或文本</h2>
                <textarea className="long-text-input" placeholder="请输入网址或长文本" value={urlText} onChange={(e) => setUrlText(e.target.value)}></textarea>
                <button className="btn" onClick={handleUrlTextUpload}>上传网址/文本</button>
                <button className="btn" style={{ marginTop: '10px' }} onClick={handleUrlTextDetection}>开始检测</button>
              </div>
            )}
            {selectedUploadType === 'audio' && (
              <div className="upload-section">
                <h2>上传通话音频</h2>
                <label htmlFor="file-upload" className="btn">选择音频文件</label>
                <input id="file-upload" type="file" onChange={handleFileChange} accept="audio/*" style={{ display: 'none' }} />
                {audioFile && (
                  <div className="file-info">
                    <span>{audioFile.name}</span>
                    <button className="remove-btn" onClick={handleRemoveFile}>×</button>
                  </div>
                )}
                <button onClick={handleSubmit} className="btn">上传并处理音频</button>
                <button className="btn" style={{ marginTop: '20px' }} onClick={handleDetection}>开始检测</button>
                <button className="btn" style={{ marginTop: '20px' }} onClick={handlesmallDetection}>开始检测(不生成方案)</button>
              </div>
            )}
            {selectedUploadType === 'emailText' && (
              <div className="upload-section">
                <h2>输入邮件文本</h2>
                <textarea className="long-text-input" placeholder="请输入邮件文本" value={emailText} onChange={(e) => setEmailText(e.target.value)}></textarea>
                <button className="btn" onClick={handleEmailUpload}>上传邮件文本</button>
                <button className="btn" style={{ marginTop: '10px' }} onClick={handleEmailDetection}>开始检测</button>
              </div>
            )}
            {result && (
              <div className="result">
                {renderDetectionData()} {/* Render the detailed detection results */}
              </div>
            )}
          </div>
        );
        case 'threat-monitoring':
        return (
          <div className="container">
            <h1>Threat Data Monitoring</h1>
            <button className="btn" onClick={handleRefreshThreatData}>刷新威胁数据</button> {/* Refresh Button */}
            {renderThreatDataList()}

      <h1>Line Chart</h1>
      <LineChart data={lineData} />

          </div>
        );
      case 'login':
        return (
          <div className="container">
            <h1>{isLoginMode ? 'Login' : 'Register'}</h1>
            <form onSubmit={handleAuthSubmit}>
              <label>Email:<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
              <label>Password:<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
              {!isLoginMode && (
                <label>Level:
                  <select value={level} onChange={(e) => setLevel(e.target.value)}>
                    <option value="VP">VP</option>
                    <option value="VVP">VVP</option>
                    <option value="User">User</option>
                    <option value="Guard">Guard</option>
                  </select>
                </label>
              )}
              <button type="submit" className="btn">{isLoginMode ? 'Login' : 'Register'}</button>
            </form>
            <p>{authResult}</p>
            <button className="btn toggle-btn" onClick={() => setIsLoginMode(!isLoginMode)}>{isLoginMode ? 'Switch to Register' : 'Switch to Login'}</button>
          </div>
        );
      case 'solutions':
          return (
            <div className="container">
              <h1>Solution Handling</h1>
              {selectedThreatFile ? (
                <div>
                  <h3>Solution Content for {selectedThreatFile}_solution.json</h3>
                  {renderFormattedSolutionContent()} {/* Display the solution content */}
                </div>
              ) : (
                <p>No solution selected.</p>
              )}
            </div>
          );
      case 'personal-information-upload':
      return (
        <div className="container">
          <h1>个人信息上传</h1>
          <form className="upload-form">
            <div className="form-group">
              <label htmlFor="profile-photo" className="file-label">上传个人照片</label>
              <input
                id="profile-photo"
                type="file"
                accept="image/*"
                onChange={handleProfilePhotoChange}
                className="file-input"
              />
            </div>
            <div className="form-group">
              <label htmlFor="audio-upload" className="file-label">上传音频信息</label>
              <input
                id="audio-upload"
                type="file"
                accept="audio/*"
                onChange={handleAudioChange}
                className="file-input"
              />
            </div>
            <div className="form-group">
              <label htmlFor="personal-introduction">个人简介</label>
              <textarea
                id="personal-introduction"
                placeholder="请输入您的个人简介"
                value={personalIntro}
                onChange={(e) => setPersonalIntro(e.target.value)}
                className="text-area"
              ></textarea>
            </div>
            <button className="btn" onClick={handlePersonalInfoUpload}>上传个人信息</button>
          </form>
        </div>
      );
      case 'company-document-upload':
        return <CompanyDocumentUpload />;
        case 're-verification':
          console.log('Rendering Identity Reverification');
          return <IdentityReverification username={email} />;
      default:
        return <div className="container"><h1>404 Page Not Found</h1></div>;
    }
  };

  const renderIdentity = () => {
    if (isLoggedIn) {
      // Define the profile images for different levels
      const profileImages: Record<'VP' | 'VVP' | 'User' | 'Guard', string> = {
        VP: '/imgs/VP.jpg',
        VVP: '/imgs/VP.jpg',
        User: '/imgs/User.jpg',
        Guard: '/imgs/Guard.jpg',
      };
  
      // Use type assertion to specify that level is one of the keys
      const profileImage = profileImages[level as 'VP' | 'VVP' | 'User' | 'Guard'] || '/imgs/User.jpg';
  
      return (
        <div className="identity">
          <img src={profileImage} alt="Profile Avatar" className="avatar" />
          <span>用户名: {email}</span>
          <span>身份: {level}</span>
        </div>
      );
    } else {
      return <div className="identity">未登录</div>;
    }
  };

  // Main return statement to render the navigation bar and content
  return (
    <div>
      {/* Navigation bar with links to different tabs */}
      <nav>
        <a href="#intro" onClick={() => handleTabClick('intro')}>介绍</a>
        <a href="#login" onClick={() => handleTabClick('login')}>登录/注册</a>
        <a href="#upload" onClick={() => handleTabClick('upload')}>上传音频</a>
        <a href="#threat-monitoring" onClick={() => handleTabClick('threat-monitoring')}>威胁分析</a>
        <a href="#face-detection" onClick={() => handleTabClick('personal-information-upload')}>上传个人信息</a>
        <a href="#audio-detection" onClick={() => handleTabClick('company-document-upload')}>上传公司章程</a>
        <a href="#re-verification" onClick={() => handleTabClick('re-verification')}>身份核验</a>
        <a href="#solutions" onClick={() => handleTabClick('solutions')}>威胁处理方案</a>
        {renderIdentity()}
      </nav>

      {/* Modal prompt for login */}
      {showLoginPrompt && (
        <div className="modal-overlay">
          <div className="modal-content">
            <p>Please log in first!</p>
            <button className="btn" onClick={() => setShowLoginPrompt(false)}>OK</button>
          </div>
        </div>
      )}

      {/* Render content based on the selected tab */}
      {renderContent()}
    </div>
  );
}
