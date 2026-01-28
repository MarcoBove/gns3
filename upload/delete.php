<?php
// delete.php - Cancella file fisico e record DB
require_once __DIR__ . '/../config.php'; // Assicurati che il percorso punti al tuo config
require_once 'templates/header.php'; // Opzionale, per mantenere lo stile se stampi messaggi

// 1. Controllo Sessione
if (empty($_SESSION['user'])) {
    header('Location: login.php');
    exit;
}

// 2. Controllo Admin (FONDAMENTALE)
if (empty($_SESSION['user']['is_admin']) || $_SESSION['user']['is_admin'] !== true) {
    http_response_code(403);
    die("Access denied: only admin can delete files.");
}

// 3. Controllo ID valido
if (!isset($_GET['id']) || empty($_GET['id'])) {
    die("ID file mancante.");
}

$fileId = $_GET['id'];

try {
    $pdo = get_db();

    // 4. Recuperiamo le info del file PRIMA di cancellarlo (ci serve il stored_name)
    $stmt = $pdo->prepare("SELECT id, stored_name, original_name FROM files WHERE id = ?");
    $stmt->execute([$fileId]);
    $file = $stmt->fetch();

    if (!$file) {
        die("File non trovato nel database.");
    }

    // 5. Cancellazione Fisica
    $filePath = STORAGE_PATH . '/' . $file['stored_name'];
    
    // Controlliamo se il file esiste fisicamente e proviamo a cancellarlo
    if (file_exists($filePath)) {
        if (!unlink($filePath)) {
            throw new Exception("Impossibile cancellare il file fisico dal server.");
        }
    } else {
        // Se il file non c'è fisicamente ma c'è nel DB, procediamo comunque a pulire il DB
        // (potresti voler loggare questo evento come warning)
    }

    // 6. Cancellazione dal Database
    $deleteStmt = $pdo->prepare("DELETE FROM files WHERE id = ?");
    $deleteStmt->execute([$fileId]);

    // 7. Redirect alla dashboard con successo
    // Se vuoi puoi passare un parametro ?msg=deleted per mostrare un alert
    header('Location: dashboard.php');
    exit;

} catch (Exception $e) {
    echo "<h2>Errore durante la cancellazione</h2>";
    echo "<p>" . htmlspecialchars($e->getMessage()) . "</p>";
    echo '<p><a href="dashboard.php">Torna alla Dashboard</a></p>';
}
?>