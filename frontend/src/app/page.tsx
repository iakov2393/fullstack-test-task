"use client";

import { useState } from "react";
import { Alert, Badge, Button, Card, Col, Container, Row } from "react-bootstrap";

import { AlertsTable } from "@/components/AlertsTable";
import { FilesTable } from "@/components/FilesTable";
import { UploadModal } from "@/components/UploadModal";
import { useFileManager } from "@/hooks/useFileManager";

export default function Page() {
  const { files, alerts, isLoading, isUploading, errorMessage, loadData, uploadFile } = useFileManager();
  const [showModal, setShowModal] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const displayedError = validationError ?? errorMessage;

  return (
    <Container fluid className="py-4 px-4 bg-light min-vh-100">
      <Row className="justify-content-center">
        <Col xxl={10} xl={11}>
          <Card className="shadow-sm border-0 mb-4">
            <Card.Body className="p-4">
              <div className="d-flex justify-content-between align-items-start gap-3 flex-wrap">
                <div>
                  <h1 className="h3 mb-2">Управление файлами</h1>
                  <p className="text-secondary mb-0">
                    Загрузка файлов, просмотр статусов обработки и ленты алертов.
                  </p>
                </div>
                <div className="d-flex gap-2">
                  <Button variant="outline-secondary" onClick={() => void loadData()}>
                    Обновить
                  </Button>
                  <Button
                    variant="primary"
                    onClick={() => {
                      setValidationError(null);
                      setShowModal(true);
                    }}
                  >
                    Добавить файл
                  </Button>
                </div>
              </div>
            </Card.Body>
          </Card>

          {displayedError ? (
            <Alert variant="danger" className="shadow-sm">
              {displayedError}
            </Alert>
          ) : null}

          <Card className="shadow-sm border-0 mb-4">
            <Card.Header className="bg-white border-0 pt-4 px-4">
              <div className="d-flex justify-content-between align-items-center">
                <h2 className="h5 mb-0">Файлы</h2>
                <Badge bg="secondary">{files.length}</Badge>
              </div>
            </Card.Header>
            <Card.Body className="px-4 pb-4">
              <FilesTable files={files} isLoading={isLoading} />
            </Card.Body>
          </Card>

          <Card className="shadow-sm border-0">
            <Card.Header className="bg-white border-0 pt-4 px-4">
              <div className="d-flex justify-content-between align-items-center">
                <h2 className="h5 mb-0">Алерты</h2>
                <Badge bg="secondary">{alerts.length}</Badge>
              </div>
            </Card.Header>
            <Card.Body className="px-4 pb-4">
              <AlertsTable alerts={alerts} isLoading={isLoading} />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <UploadModal
        show={showModal}
        isSubmitting={isUploading}
        onClose={() => setShowModal(false)}
        onSubmit={uploadFile}
        onValidationError={setValidationError}
      />
    </Container>
  );
}
