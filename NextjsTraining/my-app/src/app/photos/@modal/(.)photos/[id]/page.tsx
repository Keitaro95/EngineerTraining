export default function PhotoModal({ params }: { params: { id: string } }) {
    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <h2>Photo ID: {params.id} (Modal View)</h2>
                <p>これはモーダルとして表示されています。</p>

            </div>
        </div>
    )
}