import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import torch.nn.functional as F

# Define transformations for data augmentation and normalization
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,)) # Normalization can be modified based on dataset
])

# Load the dataset (replace with your data directory)
train_dataset = datasets.ImageFolder(root='data/train', transform=transform)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# Define CNN Model
class ScrewMeasurementNet(nn.Module):
    def __init__(self):
        super(ScrewMeasurementNet, self).__init__()
        
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1)  # 3 for RGB
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc1 = nn.Linear(64 * 16 * 16, 512)
        self.fc2 = nn.Linear(512, 128)
        self.fc3 = nn.Linear(128, 2)  # Output 2 values: width and height
        
    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        
        x = x.view(-1, 64 * 16 * 16)  # Flatten for fully connected layers
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)  # Output the width and height
        return x

# Initialize the model, loss function and optimizer
model = ScrewMeasurementNet()
criterion = nn.MSELoss()  # Mean Squared Error for regression task
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training Loop
def train_model(model, train_loader, criterion, optimizer, num_epochs=20):
    model.train()
    
    for epoch in range(num_epochs):
        running_loss = 0.0
        for images, labels in train_loader:
            # labels should be 2 values: width, height
            # Move data to GPU if available
            images, labels = images.to('cuda'), labels.float().to('cuda')
            
            # Zero the parameter gradients
            optimizer.zero_grad()
            
            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            # Backward pass and optimize
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
        
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {running_loss/len(train_loader):.4f}")

# Train the model
train_model(model, train_loader, criterion, optimizer, num_epochs=20)

# Save the trained model
torch.save(model.state_dict(), 'screw_measurement_model.pth')

# Inference code (assuming new image data)
def predict_screw_dimensions(model, image):
    model.eval()
    with torch.no_grad():
        image = transform(image).unsqueeze(0)  # Add batch dimension
        image = image.to('cuda')
        output = model(image)
        width, height = output.cpu().numpy()[0]
    return width, height
