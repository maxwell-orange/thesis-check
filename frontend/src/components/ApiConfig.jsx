import React, { useState, useEffect } from 'react';
import {
  Form,
  Select,
  Input,
  Button,
  Card,
  Space,
  Typography,
  Alert,
  Checkbox,
  Row,
  Col,
  message,
  Tooltip,
} from 'antd';
import {
  SaveOutlined,
  EyeOutlined,
  EyeInvisibleOutlined,
  KeyOutlined,
  RobotOutlined,
  CheckCircleOutlined,
  LinkOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { getProviders, saveConfig, getConfig } from '../services/api';

const { Title, Text, Link } = Typography;
const { Option } = Select;

const PROVIDER_LINKS = {
  zhipu: 'https://www.bigmodel.cn/',
  kimi: 'https://platform.moonshot.cn/',
  deepseek: 'https://platform.deepseek.com/',
  doubao: 'https://www.volcengine.com/product/doubao',
};

const PROVIDER_DESCRIPTIONS = {
  zhipu: '推荐：提供免费模型 glm-4-flash',
  kimi: '支持长文本处理',
  deepseek: '高性价比选择',
  doubao: '字节跳动出品',
};

function ApiConfig({ onConfigSaved, sessionId }) {
  const [form] = Form.useForm();
  const [providers, setProviders] = useState({});
  const [loading, setLoading] = useState(false);
  const [showApiKey, setShowApiKey] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [availableModels, setAvailableModels] = useState([]);

  useEffect(() => {
    fetchProviders();
    if (sessionId) {
      fetchExistingConfig();
    }
  }, [sessionId]);

  const fetchProviders = async () => {
    try {
      const response = await getProviders();
      if (response.data.code === 0) {
        setProviders(response.data.data);
      }
    } catch (error) {
      message.error('获取模型列表失败');
    }
  };

  const fetchExistingConfig = async () => {
    try {
      const response = await getConfig(sessionId);
      if (response.data.code === 0) {
        const config = response.data.data;
        form.setFieldsValue({
          provider: config.provider,
          model: config.model,
          enabled_checks: config.enabled_checks,
        });
        setSelectedProvider(config.provider);
        if (config.provider && providers[config.provider]) {
          setAvailableModels(providers[config.provider].models);
        }
      }
    } catch (error) {
      console.error('Failed to fetch config:', error);
    }
  };

  const handleProviderChange = (value) => {
    setSelectedProvider(value);
    if (providers[value]) {
      setAvailableModels(providers[value].models);
      form.setFieldsValue({ model: providers[value].default_model });
    }
  };

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const response = await saveConfig({
        provider: values.provider,
        api_key: values.api_key,
        model: values.model,
        enabled_checks: values.enabled_checks,
      });

      if (response.data.code === 0) {
        onConfigSaved(response.data.data);
        message.success('配置保存成功');
      } else {
        message.error(response.data.message || '保存失败');
      }
    } catch (error) {
      message.error(error.response?.data?.message || '保存失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="api-config">
      <div className="config-header">
        <div className="config-icon-wrapper">
          <KeyOutlined className="config-icon" />
        </div>
        <Title level={3} style={{ marginBottom: 8 }}>配置大模型 API</Title>
        <Text type="secondary">选择 AI 服务商并配置 API 密钥以启用智能检查</Text>
      </div>

      <Alert
        message="API 配置说明"
        description={
          <Space direction="vertical" size={4}>
            <Text>
              您的 API Key 将存储在浏览器本地，仅用于调用 AI 检查服务。
            </Text>
            <Text>
              推荐使用
              <Link href="https://www.bigmodel.cn/" target="_blank" style={{ marginLeft: 4 }}>
                智谱AI的 glm-4-flash
              </Link>
              免费模型。
            </Text>
          </Space>
        }
        type="info"
        showIcon
        style={{ marginBottom: 24, borderRadius: 12 }}
      />

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        className="config-form"
        initialValues={{
          enabled_checks: ['format', 'language', 'content', 'citation', 'references'],
        }}
      >
        <Form.Item
          name="provider"
          label={
            <Space>
              <RobotOutlined />
              <span>选择服务商</span>
            </Space>
          }
          rules={[{ required: true, message: '请选择服务商' }]}
        >
          <Select
            placeholder="请选择 AI 服务商"
            onChange={handleProviderChange}
            size="large"
            className="provider-select"
          >
            {Object.entries(providers).map(([key, value]) => (
              <Option key={key} value={key}>
                <Space>
                  <span>{value.name}</span>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {PROVIDER_DESCRIPTIONS[key]}
                  </Text>
                </Space>
              </Option>
            ))}
          </Select>
        </Form.Item>

        {selectedProvider && (
          <Form.Item style={{ marginBottom: 16 }}>
            <Card size="small" style={{ background: '#f7fafc', borderRadius: 8 }}>
              <Text type="secondary" style={{ fontSize: 13 }}>
                <InfoCircleOutlined style={{ marginRight: 8 }} />
                {PROVIDER_DESCRIPTIONS[selectedProvider]}
              </Text>
            </Card>
          </Form.Item>
        )}

        <Form.Item
          name="api_key"
          label={
            <Space>
              <KeyOutlined />
              <span>API Key</span>
            </Space>
          }
          rules={[{ required: true, message: '请输入 API Key' }]}
          tooltip="您的 API Key 仅存储在本地浏览器中"
        >
          <Input
            type={showApiKey ? 'text' : 'password'}
            placeholder="请输入您的 API Key"
            size="large"
            className="api-key-input"
            suffix={
              <Button
                type="text"
                icon={showApiKey ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                onClick={() => setShowApiKey(!showApiKey)}
              />
            }
          />
        </Form.Item>

        <Form.Item
          name="model"
          label={
            <Space>
              <RobotOutlined />
              <span>选择模型</span>
            </Space>
          }
          rules={[{ required: true, message: '请选择模型' }]}
        >
          <Select placeholder="请选择模型" size="large">
            {availableModels.map((model) => (
              <Option key={model} value={model}>
                {model}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          name="enabled_checks"
          label={
            <Space>
              <CheckCircleOutlined />
              <span>启用检查项</span>
            </Space>
          }
        >
          <Checkbox.Group style={{ width: '100%' }}>
            <Row gutter={[16, 12]}>
              <Col span={12}>
                <Checkbox value="format">
                  <Tooltip title="检查页面设置、标题格式、正文格式等">
                    <span>格式检查</span>
                  </Tooltip>
                </Checkbox>
              </Col>
              <Col span={12}>
                <Checkbox value="language">
                  <Tooltip title="检查语法错误、用词不当、语句不通顺">
                    <span>语言表达</span>
                  </Tooltip>
                </Checkbox>
              </Col>
              <Col span={12}>
                <Checkbox value="content">
                  <Tooltip title="检查摘要、章节内容、结论一致性">
                    <span>内容质量</span>
                  </Tooltip>
                </Checkbox>
              </Col>
              <Col span={12}>
                <Checkbox value="citation">
                  <Tooltip title="检查引用格式、引用与参考文献对应">
                    <span>引用规范</span>
                  </Tooltip>
                </Checkbox>
              </Col>
              <Col span={12}>
                <Checkbox value="references">
                  <Tooltip title="检查参考文献真实性、引用匹配、格式规范">
                    <span style={{ color: '#d69e2e', fontWeight: 600 }}>参考文献AI检查</span>
                  </Tooltip>
                </Checkbox>
              </Col>
            </Row>
          </Checkbox.Group>
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            icon={<SaveOutlined />}
            loading={loading}
            size="large"
            className="btn-primary-custom"
            style={{ width: '100%', height: 48 }}
          >
            保存配置
          </Button>
        </Form.Item>
      </Form>

      <Card
        title={
          <Space>
            <LinkOutlined />
            <span>服务商链接</span>
          </Space>
        }
        size="small"
        className="provider-card"
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          {Object.entries(PROVIDER_LINKS).map(([key, link]) => (
            <div key={key} className="provider-link">
              <Text strong style={{ minWidth: 100 }}>
                {providers[key]?.name || key}
              </Text>
              <Link href={link} target="_blank">
                获取 API Key →
              </Link>
            </div>
          ))}
        </Space>
      </Card>
    </div>
  );
}

export default ApiConfig;
