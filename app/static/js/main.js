// main.js - Noxco Instagram Stijl (met STL viewer fix)

document.addEventListener('DOMContentLoaded', function () {

    // === DRAG & DROP UPLOAD ===
    const uploadArea = document.getElementById('uploadArea');
    const stlInput = document.getElementById('stlFile');
    const preview = document.getElementById('uploadPreview');
    const previewImg = document.getElementById('filePreviewImage');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');

    if (uploadArea && stlInput) {
        uploadArea.addEventListener('click', () => stlInput.click());
        uploadArea.addEventListener('dragover', e => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        uploadArea.addEventListener('dragleave', e => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });
        uploadArea.addEventListener('drop', e => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                stlInput.files = e.dataTransfer.files;
                showUploadPreview(e.dataTransfer.files[0]);
            }
        });
        stlInput.addEventListener('change', function () {
            if (this.files.length) {
                showUploadPreview(this.files[0]);
            }
        });

        function showUploadPreview(file) {
            if (file && file.type.startsWith('image/')) {
                let reader = new FileReader();
                reader.onload = e => previewImg.src = e.target.result;
                reader.readAsDataURL(file);
                preview.style.display = '';
            } else {
                previewImg.src = '';
                preview.style.display = 'none';
            }
            fileName.innerText = file.name;
            fileSize.innerText = (file.size / 1024).toFixed(1) + ' KB';
        }

        const browse = uploadArea.querySelector('.browse-files');
        if (browse) browse.addEventListener('click', e => {
            e.stopPropagation();
            stlInput.click();
        });
    }

    // === PROFIELFOTO PREVIEW ===
    let picInput = document.getElementById('profile_picture_upload');
    let previewPic = document.getElementById('currentProfilePic');
    if (picInput && previewPic) {
        picInput.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                let reader = new FileReader();
                reader.onload = e => previewPic.src = e.target.result;
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    // === KLIK OP MODELKAARTEN ===
    document.querySelectorAll('.clickable-model-item, .profile-gallery-item').forEach(card => {
        card.addEventListener('click', function (event) {
            if (event.target.tagName === 'A' || event.target.closest('a')) return;
            let modelId = card.dataset.modelId;
            if (modelId) {
                window.location.href = "/model/" + modelId;
            }
        });
    });

    // === MODEL UPLOADEN KNOP ===
    const openUploadBtn = document.getElementById('openUploadModalBtn');
    if (openUploadBtn) {
        openUploadBtn.addEventListener('click', function () {
            const uploadUrl = this.dataset.uploadUrl;
            if (uploadUrl) {
                window.location.href = uploadUrl;
            } else {
                console.error("Data-upload-url niet gevonden.");
            }
        });
    }

    // === KLIK OP BERICHTEN / VRIENDEN ===
    document.querySelectorAll('.bericht-item').forEach(item => {
        item.addEventListener('click', () => {
            const berichtId = item.dataset.berichtId;
            if (berichtId) {
                window.location.href = `/bericht/${berichtId}`;
            }
        });
    });

    document.querySelectorAll('.friend-item').forEach(item => {
        item.addEventListener('click', (event) => {
            if (event.target.tagName === 'A' || event.closest('a')) return;
            const friendId = item.dataset.friendId;
            if (friendId) {
                window.location.href = `/profile/${friendId}`;
            }
        });
    });

    // === FADE-IN SCROLL EFFECT ===
    function setupFadeInOnScroll() {
        const fadeInElements = document.querySelectorAll('.fade-in-on-scroll');
        if (fadeInElements.length > 0) {
            const observer = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        observer.unobserve(entry.target);
                    }
                });
            }, { rootMargin: '0px', threshold: 0.1 });
            fadeInElements.forEach(element => observer.observe(element));
        }
    }
    setupFadeInOnScroll();

    // === TERUG-KNOP ===
    document.querySelectorAll('.terug-btn').forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            window.history.back();
        });
    });

    // === PROFIEL TABBLADEN ===
    const tabButtons = document.querySelectorAll('.profile-tabs .tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    if (tabButtons.length > 0 && tabContents.length > 0) {
        tabButtons.forEach(button => {
            button.addEventListener('click', function () {
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.style.display = 'none');
                this.classList.add('active');
                const targetTab = this.dataset.tab;
                const targetContent = document.getElementById(targetTab + '-tab-content');
                if (targetContent) {
                    targetContent.style.display = (targetTab === 'friends') ? 'flex' : 'grid';
                }
            });
        });
        const defaultTabButton = document.querySelector('.profile-tabs .tab-button[data-tab="posts"]');
        if (defaultTabButton) defaultTabButton.click();
    }

    // === STL VIEWERS OP PROFIEL ===
    const stlViewerPlaceholders = document.querySelectorAll('.stl-viewer-placeholder');
    if (stlViewerPlaceholders.length > 0) {
        stlViewerPlaceholders.forEach(placeholder => {
            const modelId = placeholder.id.replace('stl-viewer-profile-', '');
            const galleryItem = placeholder.closest('.profile-gallery-item');
            const filename = galleryItem ? galleryItem.dataset.filename : null;
            if (filename && typeof THREE !== 'undefined' && typeof THREE.STLLoader !== 'undefined') {
                initStlViewer(placeholder.id, "/static/uploads/stl_models/" + filename);
            }
        });
    }
});

// === STL VIEWER FUNCTIE ===
function initStlViewer(containerId, stlUrl) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container met ID ${containerId} niet gevonden.`);
        return;
    }

    const width = container.clientWidth;
    const height = 500;

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    container.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf3f3f3);

    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.z = 5;

    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(1, 1, 1).normalize();
    scene.add(light);

    const loader = new THREE.STLLoader();
    loader.load(stlUrl, function (geometry) {
        geometry.computeBoundingBox();
        const center = new THREE.Vector3();
        geometry.boundingBox.getCenter(center);
        geometry.translate(-center.x, -center.y, -center.z);

        const material = new THREE.MeshNormalMaterial();
        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        function animate() {
            requestAnimationFrame(animate);
            mesh.rotation.y += 0.01;
            renderer.render(scene, camera);
        }

        animate();
    }, undefined, function (error) {
        console.error("Fout bij laden STL-bestand:", error);
    });
}

// ✅ Maak globaal beschikbaar
window.initStlViewer = initStlViewer;
