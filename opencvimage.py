import cv2
img=cv2.imread('pic.jpe',1)#0,1,-1

cv2.imshow("Building",img)

cv2.waitKey(5000)
cv2.destroyAllwindows()

print(img)
