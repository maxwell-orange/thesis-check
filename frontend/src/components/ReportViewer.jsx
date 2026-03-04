import React, { useState, useEffect } from 'react';
import {
  Card,
  Tabs,
  Table,
  Tag,
  Space,
  Typography,
  Statistic,
  Row,
  Col,
  Alert,
  Badge,
  Empty,
  Spin,
  Button,
  message,
  Collapse,
} from 'antd';
import {
  WarningOutlined,
  CheckCircleOutlined,
  FileTextOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  DownloadOutlined,
  FileSearchOutlined,
  RobotOutlined,
  BookOutlined,
  LinkOutlined,
} from '@ant-design/icons';
import { getCheckReport, downloadPdfReport } from '../services/api';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;
const { Panel } = Collapse;

const ISSUE_TYPE_COLORS = {
  error: 'red',
  warning: 'orange',
  suggestion: 'blue',
};

const ISSUE_TYPE_LABELS = {
  error: '错误',
  warning: '警告',
  suggestion: '建议',
};

const CATEGORY_LABELS = {
  '页面设置': '页面设置',
  '章标题格式': '章标题',
  '节标题格式': '节标题',
  '小节标题格式': '小节标题',
  '正文格式': '正文格式',
  '摘要格式': '摘要格式',
  '参考文献格式': '参考文献',
  '参考文献真实性': '参考文献真实性',
  '引用匹配': '引用匹配',
  '格式规范': '格式规范',
  '图表格式': '图表格式',
  '内容质量': '内容质量',
  '语言表达': '语言表达',
  '引用规范': '引用规范',
};

function ReportViewer({ checkId, fileInfo }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    if (checkId) {
      fetchReport();
    }
  }, [checkId]);

  const fetchReport = async () => {
    setLoading(true);
    try {
      const response = await getCheckReport(checkId);
      if (response.data.code === 0) {
        setReport(response.data.data);
      }
    } catch (error) {
      console.error('Failed to fetch report:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!checkId) return;

    setDownloading(true);
    try {
      const response = await downloadPdfReport(checkId);

      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = url;
      const safeFilename = fileInfo?.filename?.replace('.docx', '')?.replace('.doc', '') || 'report';
      link.download = `thesis_check_report_${safeFilename}_${checkId.slice(0, 8)}.pdf`;
      document.body.appendChild(link);
      link.click();

      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      message.success('PDF报告下载成功');
    } catch (error) {
      console.error('Failed to download PDF:', error);
      message.error('PDF下载失败，请稍后重试');
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner" />
        <Text className="loading-text">加载报告中...</Text>
      </div>
    );
  }

  if (!report) {
    return (
      <Empty
        description="暂无检查报告"
        image={Empty.PRESENTED_IMAGE_SIMPLE}
      />
    );
  }

  const { format_check, ai_check, total_issues } = report;
  const formatIssues = format_check?.issues || [];
  const aiIssues = ai_check?.issues || [];

  // Separate reference-related issues
  const referenceIssues = aiIssues.filter(i =>
    i.category === '参考文献真实性' ||
    i.category === '引用匹配' ||
    i.category === '格式规范' ||
    (i.location && i.location.includes('参考文献'))
  );

  const otherAiIssues = aiIssues.filter(i => !referenceIssues.includes(i));

  const errorCount = formatIssues.filter(i => i.type === 'error').length +
                     aiIssues.filter(i => i.type === 'error').length;
  const warningCount = formatIssues.filter(i => i.type === 'warning').length +
                       aiIssues.filter(i => i.type === 'warning').length;
  const suggestionCount = formatIssues.filter(i => i.type === 'suggestion').length +
                          aiIssues.filter(i => i.type === 'suggestion').length;

  const formatColumns = [
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 90,
      render: (type) => (
        <Tag color={ISSUE_TYPE_COLORS[type]} style={{ fontWeight: 600 }}>
          {ISSUE_TYPE_LABELS[type]}
        </Tag>
      ),
    },
    {
      title: '类别',
      dataIndex: 'category',
      key: 'category',
      width: 130,
      render: (category) => CATEGORY_LABELS[category] || category,
    },
    {
      title: '位置',
      dataIndex: 'location',
      key: 'location',
      width: 180,
      ellipsis: true,
    },
    {
      title: '问题描述',
      dataIndex: 'message',
      key: 'message',
      render: (text) => <Text style={{ color: '#1a202c' }}>{text}</Text>,
    },
    {
      title: '修改建议',
      dataIndex: 'suggestion',
      key: 'suggestion',
      render: (text) => (
        <Text type="secondary" style={{ fontSize: 13 }}>{text}</Text>
      ),
    },
  ];

  const aiColumns = [
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 90,
      render: (type) => (
        <Tag color={ISSUE_TYPE_COLORS[type]} style={{ fontWeight: 600 }}>
          {ISSUE_TYPE_LABELS[type]}
        </Tag>
      ),
    },
    {
      title: '类别',
      dataIndex: 'category',
      key: 'category',
      width: 130,
      render: (category) => CATEGORY_LABELS[category] || category,
    },
    {
      title: '位置',
      dataIndex: 'location',
      key: 'location',
      width: 180,
      ellipsis: true,
    },
    {
      title: '问题描述',
      dataIndex: 'issue_description',
      key: 'issue_description',
      render: (text) => <Text style={{ color: '#1a202c' }}>{text}</Text>,
    },
    {
      title: '修改建议',
      dataIndex: 'suggestion',
      key: 'suggestion',
      render: (text) => (
        <Text type="success" style={{ fontSize: 13 }}>{text}</Text>
      ),
    },
  ];

  const expandedRowRender = (record) => (
    <div style={{ padding: '12px 0', background: '#f7fafc', borderRadius: 8, paddingLeft: 16, paddingRight: 16 }}>
      {record.original_text && (
        <Paragraph style={{ marginBottom: 12 }}>
          <Text strong style={{ color: '#4a5568' }}>原文： </Text>
          <Text style={{ fontStyle: 'italic', color: '#718096' }}>"{record.original_text}"</Text>
        </Paragraph>
      )}
      {record.corrected_text && (
        <Paragraph style={{ marginBottom: 0 }}>
          <Text strong style={{ color: '#48bb78' }}>建议修改： </Text>
          <Text style={{ color: '#2f855a' }}>{record.corrected_text}</Text>
        </Paragraph>
      )}
    </div>
  );

  return (
    <div className="report-viewer">
      <div className="report-header">
        <div className="report-title-section">
          <FileSearchOutlined className="report-icon" />
          <div>
            <Title level={3} style={{ margin: 0, fontSize: 22 }}>检查报告</Title>
            {fileInfo && (
              <Text type="secondary" style={{ fontSize: 13 }}>
                {fileInfo.filename} ({fileInfo.file_size_formatted})
              </Text>
            )}
          </div>
        </div>
        <Button
          type="primary"
          icon={<DownloadOutlined />}
          onClick={handleDownloadPdf}
          loading={downloading}
          disabled={report?.status !== 'completed'}
          className="btn-primary-custom"
          size="large"
        >
          下载PDF报告
        </Button>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <Card className="stat-card total" bordered={false}>
          <div className="stat-value">{total_issues}</div>
          <div className="stat-label">总问题数</div>
        </Card>
        <Card className="stat-card error" bordered={false}>
          <div className="stat-value">{errorCount}</div>
          <div className="stat-label">错误</div>
        </Card>
        <Card className="stat-card warning" bordered={false}>
          <div className="stat-value">{warningCount}</div>
          <div className="stat-label">警告</div>
        </Card>
        <Card className="stat-card suggestion" bordered={false}>
          <div className="stat-value">{suggestionCount}</div>
          <div className="stat-label">建议</div>
        </Card>
      </div>

      <Tabs activeKey={activeTab} onChange={setActiveTab} type="card" className="custom-tabs">
        <TabPane
          tab={
            <span>
              <InfoCircleOutlined style={{ marginRight: 6 }} />
              概览
            </span>
          }
          key="overview"
        >
          {ai_check?.summary && (
            <Card className="ai-evaluation-card" bordered={false}>
              <div className="ai-evaluation-title">
                <RobotOutlined />
                <Text strong style={{ fontSize: 16 }}>AI 总体评价</Text>
              </div>
              <Paragraph style={{ marginBottom: 0, color: '#4a5568', lineHeight: 1.8 }}>
                {ai_check.summary.overall_evaluation}
              </Paragraph>
            </Card>
          )}

          {total_issues === 0 ? (
            <Alert
              message="恭喜！未发现明显问题"
              description="论文格式规范，内容质量良好。建议您在提交前再次仔细检查。"
              type="success"
              showIcon
              style={{ borderRadius: 12 }}
            />
          ) : (
            <Alert
              message={`发现 ${total_issues} 个问题`}
              description="请点击下方标签查看详细问题列表并进行修改。重点关注错误级别的问题。"
              type="warning"
              showIcon
              style={{ borderRadius: 12 }}
            />
          )}

          {/* Quick Stats */}
          <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
            <Col span={12}>
              <Card size="small" style={{ borderRadius: 12 }}>
                <Statistic
                  title="格式问题"
                  value={formatIssues.length}
                  prefix={<FileTextOutlined />}
                  valueStyle={{ color: formatIssues.length > 0 ? '#d69e2e' : '#48bb78' }}
                />
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small" style={{ borderRadius: 12 }}>
                <Statistic
                  title="AI 检查问题"
                  value={aiIssues.length}
                  prefix={<RobotOutlined />}
                  valueStyle={{ color: aiIssues.length > 0 ? '#d69e2e' : '#48bb78' }}
                />
              </Card>
            </Col>
          </Row>
        </TabPane>

        <TabPane
          tab={
            <span>
              <FileTextOutlined style={{ marginRight: 6 }} />
              格式问题
              {formatIssues.length > 0 && (
                <Badge count={formatIssues.length} style={{ marginLeft: 8, backgroundColor: '#d69e2e' }} />
              )}
            </span>
          }
          key="format"
        >
          {formatIssues.length === 0 ? (
            <Empty description="未发现格式问题" image={Empty.PRESENTED_IMAGE_SIMPLE} />
          ) : (
            <Table
              dataSource={formatIssues}
              columns={formatColumns}
              rowKey={(record, index) => `format-${index}`}
              pagination={{ pageSize: 10 }}
              size="middle"
              className="issues-table"
            />
          )}
        </TabPane>

        <TabPane
          tab={
            <span>
              <BookOutlined style={{ marginRight: 6 }} />
              参考文献
              {referenceIssues.length > 0 && (
                <Badge count={referenceIssues.length} style={{ marginLeft: 8, backgroundColor: '#e53e3e' }} />
              )}
            </span>
          }
          key="references"
        >
          {referenceIssues.length === 0 ? (
            <Alert
              message="参考文献检查通过"
              description="未发现明显的参考文献问题。建议进一步核对引用与文献列表的对应关系。"
              type="success"
              showIcon
              style={{ borderRadius: 12 }}
            />
          ) : (
            <>
              <Alert
                message="发现参考文献相关问题"
                description="请仔细核对以下问题，确保参考文献的真实性和格式规范性"
                type="warning"
                showIcon
                style={{ marginBottom: 16, borderRadius: 12 }}
              />
              <Table
                dataSource={referenceIssues}
                columns={aiColumns}
                rowKey={(record, index) => `ref-${index}`}
                pagination={{ pageSize: 10 }}
                size="middle"
                className="issues-table"
                expandable={{
                  expandedRowRender,
                  expandRowByClick: true,
                }}
              />
            </>
          )}
        </TabPane>

        <TabPane
          tab={
            <span>
              <RobotOutlined style={{ marginRight: 6 }} />
              AI 内容检查
              {otherAiIssues.length > 0 && (
                <Badge count={otherAiIssues.length} style={{ marginLeft: 8, backgroundColor: '#3182ce' }} />
              )}
            </span>
          }
          key="ai"
        >
          {otherAiIssues.length === 0 ? (
            <Empty description="AI 检查未发现明显问题" image={Empty.PRESENTED_IMAGE_SIMPLE} />
          ) : (
            <Table
              dataSource={otherAiIssues}
              columns={aiColumns}
              rowKey={(record, index) => `ai-${index}`}
              pagination={{ pageSize: 10 }}
              size="middle"
              className="issues-table"
              expandable={{
                expandedRowRender,
                expandRowByClick: true,
              }}
            />
          )}
        </TabPane>
      </Tabs>
    </div>
  );
}

export default ReportViewer;
