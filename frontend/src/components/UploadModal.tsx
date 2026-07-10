import { FormEvent, useState } from "react";
import { Button, Form, Modal } from "react-bootstrap";

type Props = {
  show: boolean;
  isSubmitting: boolean;
  onClose: () => void;
  onSubmit: (title: string, file: File) => Promise<boolean>;
  onValidationError: (message: string) => void;
};

export function UploadModal({ show, isSubmitting, onClose, onSubmit, onValidationError }: Props) {
  const [title, setTitle] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  function reset() {
    setTitle("");
    setSelectedFile(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!title.trim() || !selectedFile) {
      onValidationError("Укажите название и выберите файл");
      return;
    }

    const success = await onSubmit(title.trim(), selectedFile);
    if (success) {
      reset();
      onClose();
    }
  }

  return (
    <Modal
      show={show}
      onHide={() => {
        reset();
        onClose();
      }}
      centered
    >
      <Form onSubmit={handleSubmit}>
        <Modal.Header closeButton>
          <Modal.Title>Добавить файл</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Group className="mb-3">
            <Form.Label>Название</Form.Label>
            <Form.Control
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Например, Договор с подрядчиком"
            />
          </Form.Group>
          <Form.Group>
            <Form.Label>Файл</Form.Label>
            <Form.Control
              type="file"
              onChange={(event) => setSelectedFile((event.target as HTMLInputElement).files?.[0] ?? null)}
            />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={onClose}>
            Отмена
          </Button>
          <Button type="submit" variant="primary" disabled={isSubmitting}>
            {isSubmitting ? "Загрузка..." : "Сохранить"}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}
