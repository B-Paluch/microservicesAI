package com.example.newproj.controllers;

import com.example.newproj.entity.FileEntity;
import com.example.newproj.entity.LogEntity;
import com.example.newproj.entity.ResponseFileEntity;
import com.example.newproj.entity.ResponseMessageEntity;
import com.example.newproj.services.FileService;
import lombok.RequiredArgsConstructor;
import org.springframework.cloud.stream.function.StreamBridge;
import org.springframework.context.annotation.Bean;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import java.util.List;
import java.util.function.Consumer;
import java.util.stream.Collectors;


@RestController
@CrossOrigin
@RequiredArgsConstructor
public class FileController {
    private final FileService service;
    private final StreamBridge streamBridge;

    @PostMapping("/upload")
    public ResponseEntity<ResponseMessageEntity> upload(@RequestParam("file") MultipartFile file) {
        var message = "";
        try {
            var entity = service.saveInDb(file);
            streamBridge.send(
                    "fileSaved-out-0",
                    LogEntity.builder().service("fileuploader").logValue("file saved:: " +
                            entity.getName().toString()
                            + " id: " + entity.getId() + ".").build()
            );

            streamBridge.send(
                    "fileCreated-out-0",
                    entity.getId());
            message = "Uploaded the file successfully: " + file.getOriginalFilename();
            return ResponseEntity.status(HttpStatus.OK).body(new ResponseMessageEntity(message));
        } catch (Exception e) {
            message = "Could not upload the file: " + e + " " + file.getOriginalFilename() + "!";
            streamBridge.send(
                    "savingFailed-out-0",
                    LogEntity.builder().service("fileuploader").logValue("Failed to save a file." +
                            e.toString()
                    ).build()
            );
            return ResponseEntity.status(HttpStatus.EXPECTATION_FAILED).body(new ResponseMessageEntity(message));
        }
    }

    @GetMapping("/files")
    public ResponseEntity<List<ResponseFileEntity>> getListFiles() {
        List<ResponseFileEntity> files = service.getAllFiles().map(file -> {
            String fileDownloadUri = ServletUriComponentsBuilder
                    .fromCurrentContextPath()
                    .path("/files/")
                    .path(file.getId())
                    .toUriString();
            streamBridge.send(
                    "fileListed-out-0",
                    LogEntity.builder().service("fileuploader").logValue("file list accessed.").build()
            );
            return new ResponseFileEntity(
                    file.getName(),
                    fileDownloadUri,
                    file.getType(),
                    file.getData().length);
        }).collect(Collectors.toList());

        return ResponseEntity.status(HttpStatus.OK).body(files);
    }

    @GetMapping("/files/{id}")
    public ResponseEntity<byte[]> getFile(@PathVariable String id) {
        FileEntity file = service.getFile(id);

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + file.getName() + "\"")
                .body(file.getData());
    }

    //sanity check, checking if message was really sent
    @Bean
    public Consumer<LogEntity> fileCreated() {
        return item -> {
            System.out.println(item.toString());
        };
    }
}
