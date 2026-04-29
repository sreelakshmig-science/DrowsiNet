        import cv2
        import dlib
        import numpy as np
        from imutils import face_utils
        from flask import Flask, render_template, Response, jsonify

            app = Flask(__name__)
            
            # Initialize Dlib
            detector = dlib.get_frontal_face_detector()
            predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

            # Global variables for status tracking
            current_status = "CAMERA OFF"
            sleep_count = 0
            
            def compute(ptA, ptB):
                return np.linalg.norm(ptA - ptB)

            def blinked(a, b, c, d, e, f):
                up = compute(b, d) + compute(c, e)
                down = compute(a, f)
                ratio = up / (2.0 * down)
                if ratio > 0.25: return 2 # Active
                elif ratio > 0.21: return 1 # Drowsy
                else: return 0 # Sleeping

        def gen_frames():
            global current_status, sleep_count
            # Using '0' for local webcam, change to your IP URL if needed
            camera = cv2.VideoCapture(0) 
            
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        
        status = "Active :)"
        color = (0, 255, 0)

        for face in faces:
            landmarks = predictor(gray, face)
            landmarks = face_utils.shape_to_np(landmarks)

            left_blink = blinked(landmarks[36], landmarks[37], landmarks[38], landmarks[41], landmarks[40], landmarks[39])
            right_blink = blinked(landmarks[42], landmarks[43], landmarks[44], landmarks[47], landmarks[46], landmarks[45])

            if left_blink == 0 or right_blink == 0:
                sleep_count += 1
                if sleep_count > 6:
                    status = "SLEEPING !!!"
                    color = (0, 0, 255)
            else:
                sleep_count = 0
                status = "Active :)"
                color = (0, 255, 0)

            # Draw rectangle and status on the frame
            (x, y, w, h) = face_utils.rect_to_bb(face)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        current_status = status # Update global status for the API
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def get_status():
    return jsonify(status=current_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
