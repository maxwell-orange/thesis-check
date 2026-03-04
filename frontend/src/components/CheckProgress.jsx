import React, { useState } from 'react';
import { Button, Progress, Card, Space, Typography, Alert, message } from 'antd';
import {
  PlayCircleOutlined,
  LoadingOutlined,
  CheckCircleFilled,
  FileSearchOutlined,
  FileTextOutlined,
  SettingOutlined,
  CheckOutlined,
  CloseCircleFilled,
} from '@ant-design/icons';
import { startCheck, getCheckStatus } from '../services/api';

const { Title, Text } = Typography;

const CHECK_STEPS = [
  {
    key: 'parse',
    title: '解析文档',
    description: '读取论文内容和格式信息',
    icon: <FileTextOutlined />,
  },
  {
    key: 'format',
    title: '格式检查',
    description: '检查页面设置、标题格式、正文格式等',
    icon: <SettingOutlined />,
  },
  {
    key: 'ai',
    title: 'AI 内容检查',
    description: '检查语言表达、学术规范、内容质量、参考文献',
    icon: <FileSearchOutlined />,
  },
  {
    key: 'report',
    title: '生成报告',
    description: '汇总检查结果',
    icon: <CheckCircleFilled />,
  },
];

function CheckProgress({ fileInfo, sessionId, onCheckStarted, onCheckComplete }) {
  const [checking, setChecking] = useState(false);
  const [checkStatus, setCheckStatus] = useState('idle');
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [checkId, setCheckId] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  const handleStartCheck = async () => {
    if (!fileInfo) {
      message.error('请先上传论文文件');
      return;
    }
    if (!sessionId) {
      message.error('请先配置 API');
      return;
    }

    setChecking(true);
    setCheckStatus('processing');
    setCurrentStep(0);
    setProgress(10);
    setErrorMessage('');

    try {
      const response = await startCheck({
        file_id: fileInfo.file_id,
        session_id: sessionId,
        check_types: ['format', 'ai'],
      });

      if (response.data.code === 0) {
        const newCheckId = response.data.data.check_id;
        setCheckId(newCheckId);
        setCurrentStep(1);
        setProgress(30);

        const completed = await pollCheckStatus(newCheckId);
        if (completed) {
          onCheckStarted({ checkId: newCheckId });
        }
      } else {
        throw new Error(response.data.message || '检查启动失败');
      }
    } catch (error) {
      setCheckStatus('failed');
      setErrorMessage(error.message || '检查失败');
      message.error(error.message || '检查失败');
    } finally {
      setChecking(false);
    }
  };

  const pollCheckStatus = async (cid) => {
    const maxAttempts = 120;
    let attempts = 0;

    return new Promise((resolve, reject) => {
      const interval = setInterval(async () => {
        attempts++;

        if (attempts > maxAttempts) {
          clearInterval(interval);
          setCheckStatus('failed');
          setErrorMessage('检查超时，请稍后刷新页面查看结果');
          message.error('检查超时');
          reject(new Error('检查超时'));
          return;
        }

        try {
          const statusResponse = await getCheckStatus(cid);

          if (statusResponse.data.code === 0) {
            const status = statusResponse.data.data;

            if (status.format_check_status === 'processing') {
              setCurrentStep(1);
              setProgress(50);
            } else if (status.format_check_status === 'completed') {
              setCurrentStep(2);
              setProgress(70);
            }

            if (status.ai_check_status === 'completed') {
              setCurrentStep(3);
              setProgress(100);
            }

            if (status.status === 'completed') {
              clearInterval(interval);
              setCheckStatus('completed');
              setCurrentStep(4);
              setProgress(100);
              onCheckComplete();
              message.success('检查完成！');
              resolve(true);
            } else if (status.status === 'failed') {
              clearInterval(interval);
              setCheckStatus('failed');
              setErrorMessage('检查过程中出现错误');
              message.error('检查失败');
              reject(new Error('检查失败'));
            }
          }
        } catch (error) {
          console.error('Poll error:', error);
        }
      }, 5000);
    });
  };

  const getStepItemClass = (index) => {
    if (currentStep > index + 1) return 'completed';
    if (currentStep === index + 1) return 'active';
    return 'pending';
  };

  if (checkStatus === 'idle') {
    return (
      <div className="check-progress">
        <div className="progress-header">
          <div className="progress-icon-wrapper">
            <PlayCircleOutlined className="progress-icon" />
          </div>
          <Title level={3} style={{ marginBottom: 8 }}>开始检查</Title>
          <Text type="secondary">准备就绪，点击下方按钮开始检查</Text>
        </div>

        <Card style={{ marginBottom: 24, borderRadius: 12 }}>
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <Text>系统将执行以下检查：</Text>
            <ul style={{ color: '#4a5568', lineHeight: 2 }}>
              <li><Text strong>格式检查：</Text> 检查页面设置、标题格式、正文格式等</li>
              <li><Text strong>AI 内容检查：</Text> 检查语言表达、学术规范、内容质量</li>
              <li><Text strong>参考文献检查：</Text> 检查真实性、引用匹配、格式规范</li>
            </ul>
          </Space>
        </Card>

        <Button
          type="primary"
          size="large"
          icon={<PlayCircleOutlined />}
          onClick={handleStartCheck}
          disabled={!fileInfo?.file_id || !sessionId}
          className="btn-primary-custom"
          style={{ width: '100%', maxWidth: 300, height: 52, fontSize: 16 }}
        >
          开始检查
        </Button>

        <div style={{ marginTop: 24 }}>
          {!fileInfo?.file_id && (
            <Alert message="请先上传论文文件" type="warning" showIcon style={{ borderRadius: 8 }} />
          )}
          {fileInfo?.file_id && !sessionId && (
            <Alert message="请先配置 API" type="warning" showIcon style={{ borderRadius: 8 }} />
          )}
          {fileInfo?.file_id && sessionId && (
            <Alert message="准备就绪，可以开始检查" type="success" showIcon style={{ borderRadius: 8 }} />
          )}
        </div>
      </div>
    );
  }

  if (checkStatus === 'failed') {
    return (
      <div className="check-progress">
        <div className="progress-header">
          <div
            className="progress-icon-wrapper"
            style={{ background: 'linear-gradient(135deg, #fed7d7, #fee' }}
          >
            <CloseCircleFilled style={{ fontSize: 40, color: '#c53030' }} />
          </div>
          <Title level={3} style={{ marginBottom: 8 }}>检查失败</Title>
        </div>

        <Alert
          message="检查过程中出现错误"
          description={errorMessage}
          type="error"
          showIcon
          style={{ marginBottom: 24, borderRadius: 12 }}
        />
        <Button onClick={() => setCheckStatus('idle')} size="large">重新检查</Button>
      </div>
    );
  }

  return (
    <div className="check-progress">
      <div className="progress-header">
        <div className="progress-icon-wrapper">
          {checkStatus === 'completed' ? (
            <CheckCircleFilled style={{ fontSize: 40, color: '#48bb78' }} />
          ) : (
            <LoadingOutlined className="progress-icon" style={{ fontSize: 40 }} />
          )}
        </div>
        <Title level={3} style={{ marginBottom: 8 }}>
          {checkStatus === 'completed' ? '检查完成' : '检查中...'}
        </Title>
        <Text type="secondary">
          {checkStatus === 'completed'
            ? '正在生成检查报告'
            : '正在分析您的论文，请稍候...'}
        </Text>
      </div>

      <div className="progress-bar-container">
        <Progress
          percent={progress}
          status={checkStatus === 'completed' ? 'success' : 'active'}
          strokeColor={{
            '0%': '#2c5282',
            '100%': '#1a365d',
          }}
          strokeWidth={12}
          showInfo={true}
          format={(percent) => <span style={{ fontWeight: 600 }}>{percent}%</span>}
        />
      </div>

      <div className="progress-steps-custom">
        {CHECK_STEPS.map((step, index) => (
          <div key={step.key} className={`progress-step-item ${getStepItemClass(index)}`}>
            <div className={`step-number ${getStepItemClass(index)}`}>
              {currentStep > index + 1 ? (
                <CheckOutlined />
              ) : (
                index + 1
              )}
            </div>
            <div className="step-content-info">
              <div className="step-title">{step.title}</div>
              <div className="step-desc">{step.description}</div>
            </div>
          </div>
        ))}
      </div>

      {checkStatus === 'completed' && (
        <Alert
          message="检查完成！"
          description="请查看检查报告，根据建议进行修改"
          type="success"
          showIcon
          style={{ borderRadius: 12 }}
        />
      )}
    </div>
  );
}

export default CheckProgress;
