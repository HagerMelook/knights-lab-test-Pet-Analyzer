import torch
import torchvision.transforms as T
from torchvision.models.segmentation import deeplabv3_resnet50
from torchvision.models import resnet50
from ultralytics import YOLO
from PIL import Image
import numpy as np
import base64
import requests
from PIL import Image as PILImage
import io

cls_model = resnet50(weights="IMAGENET1K_V1").eval()
yolo_model = YOLO("yolov5s.pt")
seg_model = deeplabv3_resnet50(weights="DEFAULT").eval()

# Load ImageNet class names
imagenet_labels = requests.get("https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt").text.splitlines()

# Determine the labels the are considered as pets
pet_labels = [
    "Chihuahua", "Japanese spaniel", "Maltese dog", "Pekinese", "Shih-Tzu", "Blenheim spaniel",
    "papillon", "toy terrier", "Rhodesian ridgeback", "Afghan hound", "basset", "beagle", "bloodhound",
    "bluetick", "black-and-tan coonhound", "Walker hound", "English foxhound", "redbone", "borzoi",
    "Irish wolfhound", "Italian greyhound", "whippet", "Ibizan hound", "Norwegian elkhound", "otterhound",
    "Saluki", "Scottish deerhound", "Weimaraner", "Staffordshire bullterrier", "American Staffordshire terrier",
    "Bedlington terrier", "Border terrier", "Kerry blue terrier", "Irish terrier", "Norfolk terrier",
    "Norwich terrier", "Yorkshire terrier", "wire-haired fox terrier", "Lakeland terrier", "Sealyham terrier",
    "Airedale", "cairn", "Australian terrier", "Dandie Dinmont", "Boston bull", "miniature schnauzer",
    "giant schnauzer", "standard schnauzer", "Scotch terrier", "Tibetan terrier", "silky terrier",
    "soft-coated wheaten terrier", "West Highland white terrier", "Lhasa", "flat-coated retriever",
    "curly-coated retriever", "golden retriever", "Labrador retriever", "Chesapeake Bay retriever",
    "German short-haired pointer", "vizsla", "English setter", "Irish setter", "Gordon setter",
    "Brittany spaniel", "clumber", "English springer", "Welsh springer spaniel", "cocker spaniel",
    "Sussex spaniel", "Irish water spaniel", "kuvasz", "schipperke", "groenendael", "malinois",
    "briard", "kelpie", "komondor", "Old English sheepdog", "Shetland sheepdog", "collie",
    "Border collie", "Bouvier des Flandres", "Rottweiler", "German shepherd", "Doberman",
    "miniature pinscher", "Greater Swiss Mountain dog", "Bernese mountain dog", "Appenzeller",
    "EntleBucher", "boxer", "bull mastiff", "Tibetan mastiff", "French bulldog", "Great Dane",
    "Saint Bernard", "Eskimo dog", "malamute", "Siberian husky", "dalmatian", "affenpinscher",
    "basenji", "pug", "Leonberg", "Newfoundland", "Great Pyrenees", "Samoyed", "Pomeranian",
    "chow", "keeshond", "Brabancon griffon", "Pembroke", "Cardigan", "toy poodle",
    "miniature poodle", "standard poodle", "Mexican hairless",
    "tabby", "tiger cat", "Persian cat", "Siamese cat", "Egyptian cat"
]


class AI_Models:
    def __init__(self, image: Image.Image):
        # convert the image to RGB image
        self.image = image.convert("RGB")
        self.cls_name = None
        self.yolo_boxes = []
        self.seg_mask = None

    def classify(self) -> bool:
        # resize the image to be size of 224 x 224 x 3
        transform = T.Compose([
            T.Resize((224, 224)),
            T.ToTensor()
        ])

        # add the axis for the batch size and set it to be 1 (single image)
        input_cls = transform(self.image).unsqueeze(0)
        with torch.no_grad():
            out_cls = cls_model(input_cls)
            cls_id = out_cls.argmax(dim = 1).item()
            self.cls_name = imagenet_labels[cls_id]
            print(self.cls_name)
        return self.cls_name in pet_labels

    def detect(self):
        yalo_results = yolo_model.predict(self.image, conf = 0.5)[0]
        self.yolo_boxes = []
        for box in yalo_results.boxes:
            # get the top-left and down-right corners
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = box.conf[0].item()
            cls = int(box.cls[0].item())
            label = yolo_model.model.names[cls]
            self.yolo_boxes.append({
                "label": label,
                "confidence": round(conf, 2),
                "box": [round(x1), round(y1), round(x2), round(y2)]
            })
        return self.yolo_boxes

    def segment(self):
        input_seg = T.ToTensor()(self.image).unsqueeze(0)
        with torch.no_grad():
            seg_output = seg_model(input_seg)['out']
        self.seg_mask = torch.argmax(seg_output.squeeze(), dim = 0).cpu().numpy()

        # Only keep cat (8) and dog (12) masks otherwise 0
        mask = np.where(np.isin(self.seg_mask, [8, 12]), self.seg_mask, 0)
        return mask

    # To allow us to send the image to the frontend
    def mask_to_base64(self, mask: np.ndarray) -> str:
        img = PILImage.fromarray((mask * 20).astype(np.uint8))  # Scale for visibility
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        base64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return base64_img
