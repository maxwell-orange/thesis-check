import React, { useState, useEffect } from 'react';
import { Layout, Card, Steps, Button, message, Typography, Alert, Space } from 'antd';
import {
  UploadOutlined,
  SettingOutlined,
  FileSearchOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import UploadForm from './components/UploadForm';
import ApiConfig from './components/ApiConfig';
import CheckProgress from './components/CheckProgress';
import ReportViewer from './components/ReportViewer';
import { healthCheck } from './services/api';
import './styles/App.css';

const { Header, Content, Footer } = Layout;
const { Title, Text, Paragraph } = Typography;

const steps = [
  {
    title: '上传论文',
    description: '上传Word文档',
    icon: <UploadOutlined />,
  },
  {
    title: '配置API',
    description: '设置AI模型',
    icon: <SettingOutlined />,
  },
  {
    title: '开始检查',
    description: '执行质量检查',
    icon: <FileSearchOutlined />,
  },
  {
    title: '查看报告',
    description: '获取检查结果',
    icon: <FileTextOutlined />,
  },
];

function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [fileInfo, setFileInfo] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [checkId, setCheckId] = useState(null);
  const [serverStatus, setServerStatus] = useState('checking');

  useEffect(() => {
    // Check server health
    healthCheck()
      .then(() => setServerStatus('ok'))
      .catch(() => setServerStatus('error'));

    // Load saved session from localStorage
    const savedSession = localStorage.getItem('thesisCheckSession');
    if (savedSession) {
      try {
        const session = JSON.parse(savedSession);
        setSessionId(session.sessionId);
      } catch (e) {
        console.error('Failed to parse session:', e);
      }
    }
  }, []);

  const handleFileUploaded = (info) => {
    setFileInfo(info);
    setCurrentStep(1);
    message.success('论文上传成功！');
  };

  const handleConfigSaved = (config) => {
    setSessionId(config.sessionId);
    localStorage.setItem('thesisCheckSession', JSON.stringify({
      sessionId: config.sessionId,
      provider: config.provider,
      model: config.model,
    }));
    setCurrentStep(2);
    message.success('API配置保存成功！');
  };

  const handleCheckStarted = (checkInfo) => {
    setCheckId(checkInfo.checkId);
    setCurrentStep(3);
  };

  const handleStepChange = (step) => {
    if (step <= currentStep) {
      setCurrentStep(step);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <UploadForm
            onFileUploaded={handleFileUploaded}
            uploadedFile={fileInfo}
          />
        );
      case 1:
        return (
          <ApiConfig
            onConfigSaved={handleConfigSaved}
            sessionId={sessionId}
          />
        );
      case 2:
        return (
          <CheckProgress
            fileInfo={fileInfo}
            sessionId={sessionId}
            onCheckStarted={handleCheckStarted}
            onCheckComplete={() => setCurrentStep(3)}
          />
        );
      case 3:
        return (
          <ReportViewer
            checkId={checkId}
            fileInfo={fileInfo}
          />
        );
      default:
        return null;
    }
  };

  return (
    <Layout className="app-layout">
      {/* Decorative background elements */}
      <div className="bg-decoration bg-decoration-1" />
      <div className="bg-decoration bg-decoration-2" />
      <div className="bg-decoration bg-decoration-3" />

      <Header className="app-header">
        <div className="header-content">
          <div className="header-brand">
            <img src="/logo2025.png" alt="学院Logo" className="header-logo-img" />
            <div className="header-divider" />
            <div className="header-title-wrap">
              <div className="header-subtitle">山东财经大学计算机与人工智能学院</div>
              <Title level={3} className="header-main-title">
                本科毕业论文检查系统
              </Title>
            </div>
          </div>
        </div>
      </Header>

      <Content className="app-content">
        {serverStatus === 'error' && (
          <Alert
            message="后端服务未启动"
            description="请确保后端服务已启动：cd backend && python app.py"
            type="error"
            showIcon
            className="server-alert"
          />
        )}

        <div className="main-container">
          {/* Progress Steps Card */}
          <Card className="steps-card" bordered={false}>
            <Steps
              current={currentStep}
              items={steps}
              onChange={handleStepChange}
              className="custom-steps"
              responsive
            />
          </Card>

          {/* Main Content Card */}
          <Card className="main-card" bordered={false}>
            <div className="step-content">
              {renderStepContent()}
            </div>
          </Card>
        </div>
      </Content>

      <Footer className="app-footer">
        <div className="footer-content">
          <div className="footer-divider" />
          <Paragraph className="footer-text">
            本科毕业论文检查系统 ©2024 山东财经大学计算机与人工智能学院
          </Paragraph>
          <Text className="footer-subtext">
            智能 · 高效 · 专业
          </Text>
        </div>
      </Footer>
    </Layout>
  );
}

export default App;
