<?php
require_once __DIR__ . '/../config.php';
require_once 'templates/header.php';
if (empty($_SESSION['user'])) { header('Location: login.php'); exit; }
$user = $_SESSION['user'];


$pdo = get_db();
$stmt = $pdo->prepare('SELECT id, original_name, size_bytes, uploaded_at FROM files ORDER BY uploaded_at DESC');
$stmt->execute();
$files = $stmt->fetchAll();
?>


<h2>Dashboard</h2>
<?php if ($user['is_admin']): ?>
<p><a href="upload.php">Upload new file (admin)</a></p>
<?php endif; ?>


<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Size</th>
            <th>Date</th>
            <th>Download</th>
            <?php if ($user['is_admin']): ?> <th>Actions</th>
            <?php endif; ?>
        </tr>
    </thead>
    <tbody>
        <?php foreach ($files as $f): ?>
            <tr>
                <td><?php echo htmlspecialchars($f['original_name']); ?></td> <td><?php echo number_format($f['size_bytes'] / 1024, 2); ?> KB</td>
                <td><?php echo htmlspecialchars($f['uploaded_at']); ?></td>
                <td><a href="download.php?id=<?php echo urlencode($f['id']); ?>">Download</a></td>
                
                <?php if ($user['is_admin']): ?> <td>
                        <a href="delete.php?id=<?php echo urlencode($f['id']); ?>" 
                           style="color: red;"
                           onclick="return confirm('Sei sicuro di voler cancellare questo file definitivamente?');">
                           Delete
                        </a>
                    </td>
                <?php endif; ?>
            </tr>
        <?php endforeach; ?>
    </tbody>
</table>


<?php require 'templates/footer.php'; ?>
