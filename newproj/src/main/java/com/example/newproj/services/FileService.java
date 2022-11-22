package com.example.newproj.services;

import com.example.newproj.entity.FileEntity;
import com.example.newproj.repositories.FileRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.stream.Stream;

@Service
@RequiredArgsConstructor
public class FileService {
    private final FileRepository repository;

    public FileEntity saveInDb(MultipartFile file) throws IOException{
        String fileName = StringUtils.cleanPath(file.getOriginalFilename());
        FileEntity savedFile = FileEntity.builder()
                .name(fileName)
                .type(file.getContentType())
                .data(file.getBytes()).build();
        return repository.save(savedFile);
    }

    public FileEntity getFile(String id){
        return repository.findById(id).get();
    }

    public Stream<FileEntity> getAllFiles(){
        return repository.findAll().stream();
    }
}
