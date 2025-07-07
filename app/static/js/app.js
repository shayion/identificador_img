const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const admin = require('firebase-admin');
const authRouter = require('./routes/auth');
const folderRouter = require('./routes/folders');
const fileUpload = require('express-fileupload');
const path = require('path');

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());
app.use(fileUpload());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

mongoose.connect(process.env.MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true
}).then(() => console.log('MongoDB conectado'))
  .catch(err => console.error('Erro ao conectar MongoDB:', err));

admin.initializeApp({
  credential: admin.credential.cert({
    projectId: process.env.FIREBASE_PROJECT_ID,
    clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
    privateKey: process.env.FIREBASE_PRIVATE_KEY.replace(/\n/g, '\n'),
  }),
});

app.use('/api/auth', authRouter);
app.use('/api/folders', folderRouter);

app.listen(process.env.PORT || 3000, () => {
  console.log(`Servidor rodando na porta ${process.env.PORT}`);
});

// backend/models/User.js
const mongoose = require('mongoose');
const UserSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true },
  password: { type: String },
  name: String,
  googleId: String
});
module.exports = mongoose.model('User', UserSchema);

// backend/models/Folder.js
const FolderSchema = new mongoose.Schema({
  name: { type: String, required: true },
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  parentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Folder', default: null },
});
module.exports = mongoose.model('Folder', FolderSchema);

// backend/routes/auth.js
const express = require('express');
const authRouter = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const admin = require('firebase-admin');
const User = require('../models/User');

authRouter.post('/register', async (req, res) => {
  const { email, password, name } = req.body;
  const existing = await User.findOne({ email });
  if (existing) return res.status(400).json({ error: 'Usuário já existe' });
  const hashed = await bcrypt.hash(password, 10);
  const user = new User({ email, password: hashed, name });
  await user.save();
  res.json({ message: 'Usuário registrado com sucesso' });
});

authRouter.post('/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (!user) return res.status(404).json({ error: 'Usuário não encontrado' });
  const isMatch = await bcrypt.compare(password, user.password);
  if (!isMatch) return res.status(400).json({ error: 'Senha incorreta' });
  const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: '1d' });
  res.json({ token, user: { id: user._id, email: user.email, name: user.name } });
});

authRouter.post('/google-login', async (req, res) => {
  const { idToken } = req.body;
  try {
    const decoded = await admin.auth().verifyIdToken(idToken);
    const { email, name, uid } = decoded;
    let user = await User.findOne({ email });
    if (!user) {
      user = new User({ email, name, googleId: uid });
      await user.save();
    }
    const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: '1d' });
    res.json({ token, user: { id: user._id, email: user.email, name: user.name } });
  } catch (error) {
    console.error(error);
    res.status(401).json({ error: 'Token inválido' });
  }
});

module.exports = authRouter;

// backend/routes/folders.js
const express = require('express');
const folderRouter = express.Router();
const Folder = require('../models/Folder');
const jwt = require('jsonwebtoken');
const fs = require('fs');
const path = require('path');

const authMiddleware = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Token não fornecido' });
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.userId = decoded.id;
    next();
  } catch {
    res.status(401).json({ error: 'Token inválido' });
  }
};

folderRouter.use(authMiddleware);

folderRouter.post('/', async (req, res) => {
  const { name, parentId } = req.body;
  const folder = new Folder({ name, parentId: parentId || null, userId: req.userId });
  await folder.save();
  res.json(folder);
});

folderRouter.get('/', async (req, res) => {
  const folders = await Folder.find({ userId: req.userId });
  res.json(folders);
});

folderRouter.post('/upload', async (req, res) => {
  if (!req.files || !req.files.file) {
    return res.status(400).json({ error: 'Nenhum arquivo enviado' });
  }
  const uploadPath = path.join(__dirname, '../uploads', req.files.file.name);
  req.files.file.mv(uploadPath, err => {
    if (err) return res.status(500).json({ error: 'Erro ao salvar arquivo' });
    res.json({ message: 'Arquivo enviado com sucesso', path: '/uploads/' + req.files.file.name });
  });
});

module.exports = folderRouter;
