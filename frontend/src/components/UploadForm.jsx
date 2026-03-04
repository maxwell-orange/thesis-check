import React, { useState } from 'react';
import { Upload, Button, message, Space, Typography, List, Tag, Card } from 'antd';
import { InboxOutlined, FileWordOutlined, DeleteOutlined, CloudUploadOutlined, FileTextOutlined } from '@ant-design/icons';
import { uploadFile, deleteFile } from '../services/api';

const { Dragger } = Upload;
const { Text, Title } = Typography;

function UploadForm({ onFileUploaded, uploadedFile }) {
  const [uploading, setUploading] = useState(false);
  const [fileList, setFileList] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState(
    uploadedFile ? [uploadedFile] : []
  );

  const handleUpload = async (file) => {
    setUploading(true);
    try {
      const response = await uploadFile(file);
      if (response.data.code === 0) {
        const fileInfo = response.data.data;
        setUploadedFiles([fileInfo]);
        onFileUploaded(fileInfo);
        message.success('文件上传成功');
      } else {
        message.error(response.data.message || '上传失败');
      }
    } catch (error) {
      message.error(error.response?.data?.message || '上传失败');
    } finally {
      setUploading(false);
    }
    return false;
  };

  const handleRemove = async (fileId) => {
    try {
      await deleteFile(fileId);
      setUploadedFiles([]);
      message.success('文件已删除');
    } catch (error) {
      message.error('删除失败');
    }
  };

  const uploadProps = {
    name: 'file',
    multiple: false,
    accept: '.docx',
    fileList,
    beforeUpload: (file) => {
      const isDocx = file.name.endsWith('.docx');
      if (!isDocx) {
        message.error('只能上传 .docx 格式的文件！');
        return Upload.LIST_IGNORE;
      }
      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error('文件大小不能超过 10MB！');
        return Upload.LIST_IGNORE;
      }
      handleUpload(file);
      return false;
    },
    onChange: (info) => {
      setFileList(info.fileList.slice(-1));
    },
  };

  return (
    <div className="upload-form">
      <div className="upload-header">
        <div className="upload-icon-wrapper">
          <CloudUploadOutlined className="upload-icon" />
        </div>
        <Title level={3} className="upload-title">上传论文文件</Title>
        <Text className="upload-subtitle">支持 .docx 格式，文件大小不超过 10MB</Text>
      </div>

      {uploadedFiles.length === 0 ? (
        <Dragger {...uploadProps} disabled={uploading} className="upload-dragger">
          <div style={{ padding: '20px 0' }}>
            <InboxOutlined className="upload-dragger-icon" />
            <Title level={4} style={{ margin: '16px 0 8px', color: '#1a365d' }}>
              点击或拖拽文件到此处上传
            </Title>
            <Text type="secondary">
              支持 .docx 格式，文件大小不超过 10MB
            </Text>
          </div>
        </Dragger>
      ) : (
        <Card className="file-list-card" bordered={false}>
          <List
            dataSource={uploadedFiles}
            renderItem={(file) => (
              <List.Item
                actions={[
                  <Button
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => handleRemove(file.file_id)}
                  >
                    删除
                  </Button>,
                ]}
              >
                <List.Item.Meta
                  avatar={
                    <div className="file-icon">
                      <FileWordOutlined style={{ fontSize: 40, color: '#1a365d' }} />
                    </div>
                  }
                  title={<div className="file-name">{file.filename}</div>}
                  description={
                    <Space className="file-meta">
                      <Tag color="blue">{file.file_size_formatted}</Tag>
                      <Tag color="green" icon={<FileTextOutlined />}>已上传</Tag>
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        </Card>
      )}

      <div className="upload-tips">
        <Title level={5} className="upload-tips-title">
          <FileTextOutlined /> 上传须知
        </Title>
        <ul>
          <li>请确保文档格式为 .docx（Word 2007 及以上版本）</li>
          <li>文档应包含：封面、摘要、目录、正文、参考文献等完整内容</li>
          <li>建议使用学校提供的论文模板进行排版</li>
          <li>系统会自动检查格式规范和内容质量</li>
        </ul>
      </div>
    </div>
  );
}

export default UploadForm;
