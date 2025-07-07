import express from 'express';
import multer from 'multer';
import fs from 'fs';
import path from 'path';
import cors from 'cors';
import { v4 as uuidv4 } from 'uuid';

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

const DATA_FILE = './files.json';

// Função para carregar metadata
function loadData() {
  if (!fs.existsSync(DATA_FILE)) return [];
  return JSON.parse(fs.readFileSync(DATA_FILE));
}

// Função para salvar metadata
function saveData(data) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
}

// Autenticação demo simples
const USERS = [
  { email: 'user1@example.com', password: '123456' },
  { email: 'user2@example.com', password: 'abcdef' },
];

// Login
app.post('/login', (req, res) => {
  const { email, password } = req.body;
  const user = USERS.find(u => u.email === email && u.password === password);
  if (!user) return res.status(401).json({ error: 'Credenciais inválidas' });
  res.json({ email: user.email });
});

// Config multer para upload em pasta por usuário
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const userEmail = req.body.userEmail;
    const userDir = path.join('uploads', userEmail);
    fs.mkdirSync(userDir, { recursive: true });
    cb(null, userDir);
  },
  filename: function (req, file, cb) {
    const uniqueName = `${Date.now()}-${file.originalname}`;
    cb(null, uniqueName);
  }
});
const upload = multer({ storage });

// Upload
app.post('/upload', upload.array('files'), (req, res) => {
  const userEmail = req.body.userEmail;
  const description = req.body.description || '';
  const filesData = loadData();

  req.files.forEach(file => {
    filesData.push({
      id: uuidv4(),
      userEmail,
      originalName: file.originalname,
      filename: file.filename,
      description,
      path: file.path,
      uploadDate: new Date()
    });
  });

  saveData(filesData);
  res.json({ message: 'Upload realizado com sucesso' });
});

// Listar arquivos, filtro por usuário e busca por texto na descrição ou nome
app.get('/files', (req, res) => {
  const { userEmail, search = '' } = req.query;
  const filesData = loadData();

  let filtered = filesData.filter(f => f.userEmail === userEmail);

  if (search) {
    const lowerSearch = search.toLowerCase();
    filtered = filtered.filter(f =>
      f.originalName.toLowerCase().includes(lowerSearch) ||
      f.description.toLowerCase().includes(lowerSearch)
    );
  }

  // Envia info dos arquivos
  res.json(filtered);
});

// Apagar arquivo
app.delete('/files/:id', (req, res) => {
  const id = req.params.id;
  let filesData = loadData();
  const fileIndex = filesData.findIndex(f => f.id === id);
  if (fileIndex === -1) return res.status(404).json({ error: 'Arquivo não encontrado' });

  const file = filesData[fileIndex];
  // Apaga arquivo do disco
  fs.unlink(file.path, err => {
    if (err) console.error('Erro ao apagar arquivo do disco:', err);
  });

  filesData.splice(fileIndex, 1);
  saveData(filesData);
  res.json({ message: 'Arquivo apagado com sucesso' });
});

// Servir arquivos estáticos (para acessar as imagens)
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});
