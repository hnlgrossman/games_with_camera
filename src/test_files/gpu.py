import cv2
import torch
import torchvision.models as models
import torchvision.transforms as transforms
import time
import numpy as np

# ========== CONFIGURATION ==========
# Set this to True to use GPU, False to use CPU
USE_GPU = True
# ===================================

# Set device based on configuration
if USE_GPU and torch.cuda.is_available():
    device = torch.device('cuda')
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")
else:
    device = torch.device('cpu')
    print(f"Using CPU")

# Load a pre-trained neural network model
model = models.resnet50(weights='IMAGENET1K_V2')
model.eval()  # Set to evaluation mode
model = model.to(device)  # Move model to selected device

# Prepare image transformation
preprocess = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Load class names
try:
    with open('imagenet_classes.txt') as f:
        classes = [line.strip() for line in f.readlines()]
except:
    classes = ['unknown'] * 1000  # Fallback if class file not found

# Initialize webcam
cap = cv2.VideoCapture(1)

# For FPS calculation
prev_frame_time = 0
new_frame_time = 0

# For performance comparison
fps_history_gpu = []
fps_history_cpu = []

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue
    
    # Calculate FPS
    new_frame_time = time.time()
    fps = 1/(new_frame_time-prev_frame_time)
    prev_frame_time = new_frame_time
    fps_int = int(fps)
    
    # Keep track of FPS values based on mode
    if USE_GPU and torch.cuda.is_available():
        fps_history_gpu.append(fps)
        if len(fps_history_gpu) > 30:
            fps_history_gpu.pop(0)
        avg_fps_gpu = sum(fps_history_gpu) / len(fps_history_gpu) if fps_history_gpu else 0
    else:
        fps_history_cpu.append(fps)
        if len(fps_history_cpu) > 30:
            fps_history_cpu.pop(0)
        avg_fps_cpu = sum(fps_history_cpu) / len(fps_history_cpu) if fps_history_cpu else 0
    
    # Create a copy for display
    display_frame = frame.copy()
    
    # Process frame with neural network
    start_time = time.time()
    
    # Preprocess the image
    input_tensor = preprocess(frame)
    input_batch = input_tensor.unsqueeze(0).to(device)  # Add batch dimension
    
    with torch.no_grad():  # No gradient calculation needed for inference
        output = model(input_batch)
    
    # Get predictions
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    top5_prob, top5_catid = torch.topk(probabilities, 5)
    
    # Move results back to CPU for display
    top5_prob = top5_prob.cpu().numpy()
    top5_catid = top5_catid.cpu().numpy()
    
    proc_time = time.time() - start_time
    
    # Display results on frame
    mode_text = "GPU" if USE_GPU and torch.cuda.is_available() else "CPU"
    cv2.putText(display_frame, f'Mode: {mode_text}', (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(display_frame, f'FPS: {fps_int}', (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(display_frame, f'Inference time: {proc_time*1000:.1f} ms', (10, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Display top 5 predictions
    for i, (prob, catid) in enumerate(zip(top5_prob, top5_catid)):
        cv2.putText(display_frame, f'{classes[catid]}: {prob*100:.1f}%', 
                   (10, 120 + 30*i), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
    
    # Display average FPS for both modes
    if fps_history_gpu:
        cv2.putText(display_frame, f'Avg GPU FPS: {avg_fps_gpu:.1f}', (10, 280), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    if fps_history_cpu:
        cv2.putText(display_frame, f'Avg CPU FPS: {avg_fps_cpu:.1f}', (10, 310), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Instructions
    cv2.putText(display_frame, 'Press G to toggle GPU/CPU', (10, display_frame.shape[0] - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(display_frame, 'Press Q to quit', (10, display_frame.shape[0] - 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Show the frame
    cv2.imshow('ResNet50 Inference - GPU vs CPU', display_frame)
    
    # Handle key presses
    key = cv2.waitKey(5) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('g'):
        # Toggle GPU usage
        USE_GPU = not USE_GPU
        print(f"Switched to {'GPU' if USE_GPU else 'CPU'} mode")
        # Move model to the appropriate device
        model = model.to(device)

cap.release()
cv2.destroyAllWindows()