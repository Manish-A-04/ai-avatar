import logging
import traceback

logging.basicConfig(level=logging.DEBUG)
from app.pipeline.lipsync.service import lipsync_service

try:
    lipsync_service.load()
except Exception as e:
    print("Caught exception at top level:")
    traceback.print_exc()

if lipsync_service._model is None:
    print("\nModel is None. Let's see the specific exception from load():")
    # Let's manually do what load() does to print the full traceback
    from app.config import settings
    import sys
    sys.path.insert(0, str(settings.wav2lip_dir))
    import torch
    from models.wav2lip import Wav2Lip
    checkpoint_path = settings.wav2lip_dir / "checkpoints" / settings.wav2lip_checkpoint
    
    try:
        checkpoint = torch.load(str(checkpoint_path), map_location="cuda")
        print("Keys in checkpoint:", list(checkpoint.keys()) if isinstance(checkpoint, dict) else type(checkpoint))
        
        model = Wav2Lip()
        model.load_state_dict(checkpoint["state_dict"])
    except Exception:
        traceback.print_exc()
